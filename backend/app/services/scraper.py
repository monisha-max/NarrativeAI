import asyncio
import hashlib
from datetime import datetime, timezone
from urllib.parse import quote_plus, urljoin

import httpx
import structlog
from bs4 import BeautifulSoup

from app.config import settings

logger = structlog.get_logger()


class ArticleScraper:
    """Scrapes articles from ET and other news sources."""

    def __init__(self):
        self.rate_limit = settings.scrape_rate_limit
        self.headers = {
            "User-Agent": settings.scrape_user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        self._semaphore = asyncio.Semaphore(5)

    async def fetch_page(self, url: str) -> str | None:
        """Fetch a single page with rate limiting."""
        async with self._semaphore:
            try:
                async with httpx.AsyncClient(
                    headers=self.headers, timeout=30, follow_redirects=True
                ) as client:
                    response = await client.get(url)
                    response.raise_for_status()
                    await asyncio.sleep(1.0 / self.rate_limit)
                    return response.text
            except Exception as e:
                logger.warning("scraper.fetch.error", url=url, error=str(e))
                return None

    def parse_et_article(self, html: str, url: str) -> dict | None:
        """Parse an Economic Times article."""
        try:
            soup = BeautifulSoup(html, "html.parser")

            # Title extraction — try multiple selectors
            title = None
            for sel in ["h1.artTitle", "h1.title", "h1"]:
                tag = soup.select_one(sel)
                if tag:
                    title = tag.get_text(strip=True)
                    break

            # Content extraction
            content = ""
            for selector in [
                "div.artText",
                "div.Normal",
                "div.article-body",
                "div.story_content",
                "article",
                "div.content",
            ]:
                body = soup.select_one(selector)
                if body:
                    paragraphs = body.find_all("p")
                    content = "\n\n".join(
                        p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)
                    )
                    if content:
                        break

            # Fallback: get all paragraphs from main content area
            if not content:
                main = soup.find("main") or soup.find("article") or soup
                paragraphs = main.find_all("p")
                content = "\n\n".join(
                    p.get_text(strip=True)
                    for p in paragraphs
                    if len(p.get_text(strip=True)) > 40
                )

            if not title or not content or len(content) < 100:
                return None

            # Publish date
            published_at = None
            time_tag = soup.find("time")
            if time_tag and time_tag.get("datetime"):
                published_at = time_tag["datetime"]
            else:
                # Try meta tags
                for meta_name in ["article:published_time", "datePublished", "pubdate"]:
                    meta = soup.find("meta", attrs={"property": meta_name}) or soup.find(
                        "meta", attrs={"name": meta_name}
                    )
                    if meta and meta.get("content"):
                        published_at = meta["content"]
                        break

            # Author
            author = None
            for sel in [".author-name", ".byline", "[rel='author']", ".artByline"]:
                tag = soup.select_one(sel)
                if tag:
                    author = tag.get_text(strip=True).replace("By ", "").replace("by ", "")
                    break

            # Tags/keywords
            tags = []
            keywords_meta = soup.find("meta", attrs={"name": "keywords"})
            if keywords_meta and keywords_meta.get("content"):
                tags = [t.strip() for t in keywords_meta["content"].split(",")][:10]

            # Summary/description
            summary = None
            desc_meta = soup.find("meta", attrs={"name": "description"}) or soup.find(
                "meta", attrs={"property": "og:description"}
            )
            if desc_meta and desc_meta.get("content"):
                summary = desc_meta["content"]

            # Content hash for dedup
            content_hash = hashlib.sha256(content.encode()).hexdigest()

            return {
                "title": title,
                "url": url,
                "content": content,
                "summary": summary,
                "published_at": published_at,
                "author": author,
                "tags": tags,
                "content_hash": content_hash,
            }
        except Exception as e:
            logger.warning("scraper.parse.error", url=url, error=str(e))
            return None

    async def scrape_article(self, url: str) -> dict | None:
        """Fetch and parse a single article."""
        html = await self.fetch_page(url)
        if html:
            return self.parse_et_article(html, url)
        return None

    async def search_et(self, query: str, max_results: int = 50) -> list[str]:
        """Search Economic Times for article URLs matching a query.

        Uses ET's search page to find relevant articles.
        """
        urls = []
        encoded_query = quote_plus(query)

        # ET search URL pattern
        search_url = f"https://economictimes.indiatimes.com/searchresult.cms?query={encoded_query}"

        html = await self.fetch_page(search_url)
        if not html:
            return urls

        soup = BeautifulSoup(html, "html.parser")

        # Extract article links from search results
        for link in soup.select("a[href]"):
            href = link.get("href", "")
            # Filter for article URLs (typically contain /articleshow/ or /news/)
            if any(
                pattern in href
                for pattern in ["/articleshow/", "/news/", "/markets/", "/industry/"]
            ):
                full_url = href if href.startswith("http") else urljoin("https://economictimes.indiatimes.com", href)
                if full_url not in urls:
                    urls.append(full_url)
                    if len(urls) >= max_results:
                        break

        logger.info("scraper.search.results", query=query, urls_found=len(urls))
        return urls

    async def search_google_news(self, query: str, site: str = "economictimes.indiatimes.com", max_results: int = 30) -> list[str]:
        """Search via Google News RSS for articles from a specific site."""
        import feedparser

        encoded_query = quote_plus(f"{query} site:{site}")
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"

        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=30) as client:
                response = await client.get(rss_url)
                response.raise_for_status()

            feed = feedparser.parse(response.text)
            urls = []
            for entry in feed.entries[:max_results]:
                link = entry.get("link", "")
                if link:
                    urls.append(link)

            logger.info("scraper.google_news.results", query=query, urls_found=len(urls))
            return urls
        except Exception as e:
            logger.warning("scraper.google_news.error", error=str(e))
            return []

    async def bulk_scrape(self, urls: list[str]) -> list[dict]:
        """Scrape multiple URLs concurrently."""
        tasks = [self.scrape_article(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        articles = []
        for result in results:
            if isinstance(result, dict) and result is not None:
                articles.append(result)

        logger.info("scraper.bulk.complete", total=len(urls), successful=len(articles))
        return articles

    def compute_relevance_score(self, article: dict, query: str) -> float:
        """Score article relevance to the query (0-1)."""
        score = 0.0
        query_terms = query.lower().split()
        title = (article.get("title") or "").lower()
        content = (article.get("content") or "").lower()

        # Title matches are weighted heavily
        title_matches = sum(1 for term in query_terms if term in title)
        score += (title_matches / max(len(query_terms), 1)) * 0.5

        # Content matches
        content_matches = sum(1 for term in query_terms if term in content)
        score += (content_matches / max(len(query_terms), 1)) * 0.3

        # Content length bonus (longer articles tend to be more substantive)
        content_len = len(content)
        if content_len > 2000:
            score += 0.1
        if content_len > 5000:
            score += 0.1

        return min(score, 1.0)


scraper = ArticleScraper()
