from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class CalendarEventLink(Base):
    __tablename__ = "calendar_event_links"
    __table_args__ = (UniqueConstraint("registration_id", name="uq_calendar_link_registration"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    registration_id: Mapped[int] = mapped_column(ForeignKey("event_registrations.id"), index=True)

    provider: Mapped[str] = mapped_column(String(32), index=True)
    calendar_id: Mapped[str] = mapped_column(String(128), default="primary")
    provider_event_id: Mapped[str] = mapped_column(String(256), index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

