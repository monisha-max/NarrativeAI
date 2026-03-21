from fastapi import APIRouter

from app.services.delta import delta_engine

router = APIRouter()


@router.get("/{user_id}/all")
async def get_all_deltas(user_id: str):
    """Get delta cards for all followed dossiers."""
    return await delta_engine.get_all_deltas(user_id)


@router.get("/{user_id}/{dossier_slug}")
async def get_delta(user_id: str, dossier_slug: str):
    """Get what changed for a specific dossier since the user's last visit."""
    return await delta_engine.get_delta(user_id, dossier_slug)
