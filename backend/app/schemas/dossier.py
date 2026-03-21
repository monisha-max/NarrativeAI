from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DossierEventOut(BaseModel):
    id: UUID
    event_type: str
    title: str
    summary: str
    occurred_at: datetime
    entities_involved: list[str] | None = None
    sentiment_scores: dict | None = None
    market_impact: float | None = None
    fog_density: float = 0.5

    model_config = {"from_attributes": True}


class DossierOut(BaseModel):
    id: UUID
    title: str
    slug: str
    description: str | None = None
    status: str
    velocity: str
    article_count: int
    tags: list[str] | None = None
    created_at: datetime
    updated_at: datetime
    events: list[DossierEventOut] = []

    model_config = {"from_attributes": True}


class DossierListOut(BaseModel):
    dossiers: list[DossierOut]
    total: int


class DossierCreateIn(BaseModel):
    title: str
    description: str | None = None
    tags: list[str] | None = None
