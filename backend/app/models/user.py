from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(255), unique=True)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    user_type: Mapped[str] = mapped_column(String(100), default="retail_investor")
    # student, retail_investor, founder, cfo, policy, journalist
    language: Mapped[str] = mapped_column(String(10), default="en")
    perspective_settings: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # {"risk": 0.5, "stakeholder": "investor", "sentiment": 0.5, "geography": 0.5, "depth": 0.5}

    sessions: Mapped[list["UserSession"]] = relationship(back_populates="user")
    followed_dossiers: Mapped[list["FollowedDossier"]] = relationship(back_populates="user")


class UserSession(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "user_sessions"

    user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    dossier_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("dossiers.id"))
    last_read_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    read_event_ids: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # list of event IDs
    delta_state: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    user: Mapped["User"] = relationship(back_populates="sessions")


class FollowedDossier(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "followed_dossiers"

    user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    dossier_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("dossiers.id"))
    notification_prefs: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # {"any_update": false, "major_only": true, "phase_transitions": true, "silence_alerts": true}

    user: Mapped["User"] = relationship(back_populates="followed_dossiers")
