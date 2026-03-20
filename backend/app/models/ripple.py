from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class RippleConnection(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ripple_connections"

    source_dossier_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("dossiers.id"))
    target_dossier_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("dossiers.id"))
    connection_type: Mapped[str] = mapped_column(String(100))  # entity, sector, regulatory, financial
    strength: Mapped[float] = mapped_column(Float, default=0.5)
    shared_entities: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


class RippleAlert(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ripple_alerts"

    source_dossier_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("dossiers.id"))
    target_dossier_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("dossiers.id"))
    trigger_event_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("dossier_events.id"))
    impact_description: Mapped[str] = mapped_column(Text)
    magnitude: Mapped[float] = mapped_column(Float, default=0.5)
    status: Mapped[str] = mapped_column(String(50), default="active")  # active, dismissed, confirmed
