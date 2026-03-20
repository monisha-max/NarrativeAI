from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class Entity(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "entities"

    name: Mapped[str] = mapped_column(String(512), index=True)
    entity_type: Mapped[str] = mapped_column(String(100))  # company, person, regulator, investor, sector
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    aliases: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # {"aliases": ["Byju's", "BJYU", "Think & Learn"]}
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)


class EntityRelationship(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "entity_relationships"

    source_entity_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("entities.id"))
    target_entity_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("entities.id"))
    relationship_type: Mapped[str] = mapped_column(String(100))  # ownership, regulatory, legal, financial, employment, partnership, competitor
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    details: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    dossier_id: Mapped[str | None] = mapped_column(UUID(as_uuid=True), ForeignKey("dossiers.id"), nullable=True)
