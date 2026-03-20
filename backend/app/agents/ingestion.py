import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.db.session import async_session
from app.models.article import Article, Source
from app.services.scraper import scraper
from app.services.elasticsearch import search_service, ARTICLE_INDEX


class IngestionAgent(BaseAgent):
    """Crawls articles, filings, and social signals. Handles dedup and relevance scoring."""

    name = "ingestion"

    async def execute(self, context: AgentContext) -> AgentResult:
        query = context.query or context.data.get("query", "")
        dossier_id = context.dossier_id
        max_articles = context.data.get("max_articles", 50)

        if not query:
            return AgentResult(
                agent_name=self.name,
                success=False,
                error="No query provided for ingestion",
            )

        self.logger.info("ingestion.start", query=query, dossier_id=dossier_id)

        # Phase 1: Discover article URLs from multiple sources
        urls = set()

        # Search ET directly
        et_urls = await scraper.search_et(query, max_results=max_articles)
        urls.update(et_urls)

        # Search Google News for ET articles
        google_urls = await scraper.search_google_news(query, max_results=20)
        urls.update(google_urls)

        self.logger.info("ingestion.urls_discovered", count=len(urls))

        if not urls:
            # If no URLs found via search, check if we have pre-loaded corpus data
            return AgentResult(
                agent_name=self.name,
                success=True,
                data={
                    "articles_found": 0,
                    "articles_new": 0,
                    "query": query,
                    "message": "No articles found via search. Consider loading corpus data.",
                },
            )

        # Phase 2: Scrape articles
        articles = await scraper.bulk_scrape(list(urls)[:max_articles])

        # Phase 3: Score relevance and filter
        scored_articles = []
        for article in articles:
            score = scraper.compute_relevance_score(article, query)
            if score >= 0.2:  # Minimum relevance threshold
                article["relevance_score"] = score
                scored_articles.append(article)

        scored_articles.sort(key=lambda a: a["relevance_score"], reverse=True)
        self.logger.info("ingestion.relevant_articles", count=len(scored_articles))

        # Phase 4: Deduplicate and store
        new_articles = []
        async with async_session() as db:
            # Ensure ET source exists
            source = await self._get_or_create_source(db, "Economic Times", "https://economictimes.indiatimes.com", "web")

            for article_data in scored_articles:
                # Check for duplicates by URL
                existing = await db.execute(
                    select(Article).where(Article.url == article_data["url"])
                )
                if existing.scalar_one_or_none():
                    continue

                # Parse published_at
                published_at = self._parse_date(article_data.get("published_at"))

                # Create article record
                article = Article(
                    title=article_data["title"],
                    url=article_data["url"],
                    content=article_data["content"],
                    summary=article_data.get("summary"),
                    published_at=published_at,
                    author=article_data.get("author"),
                    source_id=source.id,
                    tags=article_data.get("tags"),
                    dossier_id=uuid.UUID(dossier_id) if dossier_id else None,
                )
                db.add(article)
                await db.flush()

                # Index in Elasticsearch
                try:
                    await search_service.index_article(
                        str(article.id),
                        {
                            "title": article.title,
                            "content": article.content,
                            "summary": article.summary,
                            "url": article.url,
                            "published_at": published_at.isoformat() if published_at else None,
                            "author": article.author,
                            "source_name": "Economic Times",
                            "dossier_slug": context.data.get("dossier_slug"),
                            "tags": article.tags or [],
                            "entities": [],  # Will be filled by Entity Agent
                        },
                    )
                except Exception as e:
                    self.logger.warning("ingestion.es_index.error", error=str(e))

                new_articles.append({
                    "id": str(article.id),
                    "title": article.title,
                    "url": article.url,
                    "published_at": published_at.isoformat() if published_at else None,
                    "relevance_score": article_data["relevance_score"],
                    "content_length": len(article.content),
                })

            await db.commit()

        self.logger.info(
            "ingestion.complete",
            discovered=len(urls),
            scraped=len(articles),
            relevant=len(scored_articles),
            new=len(new_articles),
        )

        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "articles_found": len(scored_articles),
                "articles_new": len(new_articles),
                "articles": new_articles,
                "query": query,
            },
        )

    async def _get_or_create_source(self, db: AsyncSession, name: str, url: str, source_type: str) -> Source:
        """Get or create a source record."""
        result = await db.execute(select(Source).where(Source.url == url))
        source = result.scalar_one_or_none()
        if not source:
            source = Source(name=name, url=url, source_type=source_type, reliability_score=0.8)
            db.add(source)
            await db.flush()
        return source

    def _parse_date(self, date_str: str | None) -> datetime:
        """Parse various date formats into datetime."""
        if not date_str:
            return datetime.now(timezone.utc)

        # Try multiple formats
        formats = [
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S.%f%z",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%b %d, %Y %H:%M %p",
            "%B %d, %Y",
            "%d %b %Y",
            "%d %B %Y",
        ]

        for fmt in formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except ValueError:
                continue

        # Fallback: try dateutil
        try:
            from dateutil import parser as dateutil_parser
            dt = dateutil_parser.parse(date_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except Exception:
            return datetime.now(timezone.utc)
