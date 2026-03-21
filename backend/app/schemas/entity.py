from uuid import UUID

from pydantic import BaseModel


class EntityOut(BaseModel):
    id: UUID
    name: str
    entity_type: str
    description: str | None = None
    aliases: dict | None = None

    model_config = {"from_attributes": True}


class EntityRelationshipOut(BaseModel):
    id: UUID
    source_entity_id: UUID
    target_entity_id: UUID
    relationship_type: str
    weight: float
    details: dict | None = None

    model_config = {"from_attributes": True}


class EntityGraphOut(BaseModel):
    entities: list[EntityOut]
    relationships: list[EntityRelationshipOut]
