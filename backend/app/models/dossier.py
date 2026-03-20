from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Dossier(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "dossiers"

    title: Mapped[str] = mapped_column(String(512))
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active")  # active, archived
    velocity: Mapped[str] = mapped_column(String(50), default="moderate")  # slow, moderate, rapid, crisis
    article_count: Mapped[int] = mapped_column(Integer, default=0)
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)

    # Relationships
    events: Mapped[list["DossierEvent"]] = relationship(back_populates="dossier", order_by="DossierEvent.occurred_at")
    story_dna: Mapped["StoryDNA | None"] = relationship(back_populates="dossier")

    @property
    def url_path(self) -> str:
        return f"/dossier/{self.slug}"


class DossierEvent(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "dossier_events"

    dossier_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("dossiers.id"))
    event_type: Mapped[str] = mapped_column(String(100))  # corporate, regulatory, financial, management, market, legal
    title: Mapped[str] = mapped_column(String(512))
    summary: Mapped[str] = mapped_column(Text)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    source_article_ids: Mapped[list[str] | None] = mapped_column(ARRAY(UUID(as_uuid=True)), nullable=True)
    entities_involved: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    sentiment_scores: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    market_impact: Mapped[float | None] = mapped_column(Float, nullable=True)
    fog_density: Mapped[float] = mapped_column(Float, default=0.5)  # 0=clear, 1=foggy

    dossier: Mapped["Dossier"] = relationship(back_populates="events")
