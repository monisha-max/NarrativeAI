"""Bulk ingest pre-scraped articles for demo dossiers."""

import asyncio

from app.db.session import engine
from app.models.base import Base


async def ingest():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # TODO: Implement bulk ingestion
    # 1. Read from data/corpus/ directory
    # 2. Parse articles
    # 3. Run entity extraction
    # 4. Index in Elasticsearch
    # 5. Store in PostgreSQL
    print("Corpus ingestion: not yet implemented")
    print("Add article JSON files to backend/data/corpus/ and re-run")


if __name__ == "__main__":
    asyncio.run(ingest())
