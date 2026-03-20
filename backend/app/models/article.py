from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Source(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "sources"

    name: Mapped[str] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(String(1024), unique=True)
    source_type: Mapped[str] = mapped_column(String(50))  # rss, web, filing, social
    reliability_score: Mapped[float] = mapped_column(Float, default=0.5)

    articles: Mapped[list["Article"]] = relationship(back_populates="source")


class Article(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "articles"

    title: Mapped[str] = mapped_column(String(1024))
    url: Mapped[str] = mapped_column(String(2048), unique=True)
    content: Mapped[str] = mapped_column(Text)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("sources.id"))
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    dossier_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dossiers.id"), nullable=True
    )

    source: Mapped["Source"] = relationship(back_populates="articles")
