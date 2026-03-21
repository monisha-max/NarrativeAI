import structlog

from app.config import settings

logger = structlog.get_logger()

ARTICLE_INDEX = "narrativeai_articles"


class SearchService:
    """Elasticsearch service for article search and indexing. Gracefully degrades if ES is unavailable."""

    def __init__(self):
        self.client = None
        self.available = False
        if settings.elasticsearch_url:
            try:
                from elasticsearch import AsyncElasticsearch
                self.client = AsyncElasticsearch(settings.elasticsearch_url)
                self.available = True
            except Exception as e:
                logger.warning("elasticsearch.init.failed", error=str(e))

    async def init_index(self):
        if not self.available:
            return
        try:
            exists = await self.client.indices.exists(index=ARTICLE_INDEX)
            if not exists:
                await self.client.indices.create(
                    index=ARTICLE_INDEX,
                    body={
                        "mappings": {
                            "properties": {
                                "title": {"type": "text", "analyzer": "standard"},
                                "content": {"type": "text", "analyzer": "standard"},
                                "summary": {"type": "text"},
                                "url": {"type": "keyword"},
                                "published_at": {"type": "date"},
                                "author": {"type": "keyword"},
                                "source_name": {"type": "keyword"},
                                "dossier_slug": {"type": "keyword"},
                                "tags": {"type": "keyword"},
                                "entities": {"type": "keyword"},
                            }
                        }
                    },
                )
                logger.info("elasticsearch.index.created", index=ARTICLE_INDEX)
        except Exception as e:
            logger.warning("elasticsearch.init_index.failed", error=str(e))
            self.available = False

    async def index_article(self, article_id: str, doc: dict):
        if not self.available:
            return
        try:
            await self.client.index(index=ARTICLE_INDEX, id=article_id, document=doc)
        except Exception as e:
            logger.warning("elasticsearch.index.failed", error=str(e))

    async def search_articles(
        self,
        query: str,
        dossier_slug: str | None = None,
        limit: int = 20,
    ) -> list[dict]:
        if not self.available:
            return []
        try:
            must = [{"multi_match": {"query": query, "fields": ["title^3", "content", "summary"]}}]
            if dossier_slug:
                must.append({"term": {"dossier_slug": dossier_slug}})

            result = await self.client.search(
                index=ARTICLE_INDEX,
                body={
                    "query": {"bool": {"must": must}},
                    "size": limit,
                    "sort": [{"published_at": {"order": "desc"}}],
                },
            )
            return [hit["_source"] | {"_id": hit["_id"], "_score": hit["_score"]} for hit in result["hits"]["hits"]]
        except Exception as e:
            logger.warning("elasticsearch.search.failed", error=str(e))
            return []

    async def close(self):
        if self.client:
            await self.client.close()


search_service = SearchService()
