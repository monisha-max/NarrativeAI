from uuid import UUID

from pydantic import BaseModel


class ArchetypePhaseOut(BaseModel):
    phase_number: int
    name: str
    description: str
    typical_duration_days: int | None = None
    transition_indicators: list[str] | None = None

    model_config = {"from_attributes": True}


class ArchetypeOut(BaseModel):
    id: UUID
    name: str
    slug: str
    description: str
    icon: str | None = None
    avg_duration_months: int
    reference_cases: list[str] | None = None
    phases: list[ArchetypePhaseOut] = []

    model_config = {"from_attributes": True}


class StoryDNAOut(BaseModel):
    archetype: ArchetypeOut
    current_phase: int
    confidence: float
    phase_prediction: dict | None = None
    silence_alert: dict | None = None

    model_config = {"from_attributes": True}
