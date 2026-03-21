from datetime import datetime

from pydantic import BaseModel


class DeltaCard(BaseModel):
    dossier_slug: str
    dossier_title: str
    new_events_count: int
    change_summary: str
    sentiment_shift: dict | None = None
    new_entities: list[str] = []
    predictions_tested: list[str] = []
    phase_change: bool = False
    velocity_change: str | None = None
    ripple_alerts: list[str] = []
    significance_score: float = 0.0
    last_checked: datetime | None = None


class DeltaResponse(BaseModel):
    cards: list[DeltaCard]
    sixty_second_summary: dict | None = None
