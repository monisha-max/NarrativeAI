from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class RippleConnectionOut(BaseModel):
    source_dossier_id: UUID
    target_dossier_id: UUID
    connection_type: str
    strength: float
    shared_entities: dict | None = None
    description: str | None = None

    model_config = {"from_attributes": True}


class RippleAlertOut(BaseModel):
    id: UUID
    source_dossier_id: UUID
    target_dossier_id: UUID
    impact_description: str
    magnitude: float
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
