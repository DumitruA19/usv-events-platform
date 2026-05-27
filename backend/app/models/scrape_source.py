from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ScrapeSource(Base):
    __tablename__ = "scrape_sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(1024), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    fail_count: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

