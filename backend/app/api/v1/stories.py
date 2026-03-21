from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.archetype import Archetype, StoryDNA
from app.models.dossier import Dossier
from app.schemas.story_dna import ArchetypeOut, StoryDNAOut

router = APIRouter()


@router.get("/archetypes", response_model=list[ArchetypeOut])
async def list_archetypes(db: AsyncSession = Depends(get_db)):
    """List all story archetypes in the library."""
    result = await db.execute(
        select(Archetype).options(selectinload(Archetype.phases))
    )
    return result.scalars().all()


@router.get("/dna/{dossier_slug}", response_model=StoryDNAOut)
async def get_story_dna(dossier_slug: str, db: AsyncSession = Depends(get_db)):
    """Get Story DNA (archetype, phase, prediction) for a dossier."""
    dossier_result = await db.execute(select(Dossier.id).where(Dossier.slug == dossier_slug))
    dossier_id = dossier_result.scalar_one_or_none()
    if not dossier_id:
        raise HTTPException(status_code=404, detail="Dossier not found")

    dna_result = await db.execute(
        select(StoryDNA)
        .where(StoryDNA.dossier_id == dossier_id)
        .options(selectinload(StoryDNA.archetype).selectinload(Archetype.phases))
    )
    dna = dna_result.scalar_one_or_none()
    if not dna:
        raise HTTPException(status_code=404, detail="Story DNA not yet computed for this dossier")

    return StoryDNAOut(
        archetype=dna.archetype,
        current_phase=dna.current_phase,
        confidence=dna.confidence,
        phase_prediction=dna.phase_prediction,
        silence_alert=dna.last_silence_check,
    )
