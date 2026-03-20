from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Archetype(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "archetypes"

    name: Mapped[str] = mapped_column(String(255), unique=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True)
    description: Mapped[str] = mapped_column(Text)
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)
    avg_duration_months: Mapped[int] = mapped_column(Integer, default=12)
    reference_cases: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)

    phases: Mapped[list["ArchetypePhase"]] = relationship(
        back_populates="archetype", order_by="ArchetypePhase.phase_number"
    )


class ArchetypePhase(Base, UUIDMixin):
    __tablename__ = "archetype_phases"

    archetype_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("archetypes.id"))
    phase_number: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    typical_duration_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    transition_indicators: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)

    archetype: Mapped["Archetype"] = relationship(back_populates="phases")


class StoryDNA(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "story_dna"

    dossier_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dossiers.id"), unique=True
    )
    archetype_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("archetypes.id"))
    current_phase: Mapped[int] = mapped_column(Integer, default=1)
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    phase_prediction: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # e.g. {"next_phase": 4, "probability": 0.8, "estimated_days": 60, "trigger_events": [...]}
    silence_baseline_days: Mapped[float | None] = mapped_column(Float, nullable=True)
    last_silence_check: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    dossier: Mapped["Dossier"] = relationship(back_populates="story_dna")
    archetype: Mapped["Archetype"] = relationship()
