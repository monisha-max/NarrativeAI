from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.entity import Entity, EntityRelationship
from app.schemas.entity import EntityGraphOut, EntityOut

router = APIRouter()


@router.get("/", response_model=list[EntityOut])
async def list_entities(
    entity_type: str | None = None,
    search: str | None = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """List entities, optionally filtered by type or search term."""
    query = select(Entity).limit(limit)
    if entity_type:
        query = query.where(Entity.entity_type == entity_type)
    if search:
        query = query.where(Entity.name.ilike(f"%{search}%"))
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/graph/{dossier_slug}", response_model=EntityGraphOut)
async def get_entity_graph(dossier_slug: str, db: AsyncSession = Depends(get_db)):
    """Get the entity relationship graph (Money Map) for a dossier."""
    from app.models.dossier import Dossier

    # Get dossier ID
    dossier_result = await db.execute(select(Dossier.id).where(Dossier.slug == dossier_slug))
    dossier_id = dossier_result.scalar_one_or_none()
    if not dossier_id:
        raise HTTPException(status_code=404, detail="Dossier not found")

    # Get relationships for this dossier
    rels_result = await db.execute(
        select(EntityRelationship).where(EntityRelationship.dossier_id == dossier_id)
    )
    relationships = rels_result.scalars().all()

    # Collect unique entity IDs
    entity_ids = set()
    for rel in relationships:
        entity_ids.add(rel.source_entity_id)
        entity_ids.add(rel.target_entity_id)

    # Fetch entities
    entities = []
    if entity_ids:
        ent_result = await db.execute(select(Entity).where(Entity.id.in_(entity_ids)))
        entities = ent_result.scalars().all()

    return EntityGraphOut(entities=entities, relationships=relationships)
