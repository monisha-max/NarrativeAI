from fastapi import APIRouter

from app.services.elasticsearch import search_service

router = APIRouter()


@router.get("/")
async def search_articles(
    q: str,
    dossier: str | None = None,
    limit: int = 20,
):
    """Full-text search across all articles."""
    results = await search_service.search_articles(
        query=q,
        dossier_slug=dossier,
        limit=limit,
    )
    return {"results": results, "query": q, "total": len(results)}
