from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    username: Mapped[str | None] = mapped_column(String(64), unique=True, index=True, nullable=True)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None, nullable=True)

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), index=True)

    role = relationship("Role", back_populates="users")
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False)
    organizer_profile = relationship("OrganizerProfile", back_populates="user", uselist=False)

    organized_events = relationship("Event", back_populates="organizer", foreign_keys="Event.organizer_id")

