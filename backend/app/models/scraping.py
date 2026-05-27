from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.enums import ScrapedDraftStatus


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ScrapedEventDraft(Base):
    __tablename__ = "scraped_event_drafts"

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(128), index=True)
    status: Mapped[ScrapedDraftStatus] = mapped_column(String(16), index=True, default=ScrapedDraftStatus.PENDING)
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    raw_payload_json: Mapped[str] = mapped_column(Text)

    title: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    start_dt: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    end_dt: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    location_text: Mapped[str | None] = mapped_column(String(255), nullable=True)
    category_text: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    approved_by_admin_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    approved_event_id: Mapped[int | None] = mapped_column(ForeignKey("events.id"), nullable=True)

