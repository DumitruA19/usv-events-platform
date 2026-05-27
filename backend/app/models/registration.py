from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import RegistrationStatus


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class EventRegistration(Base):
    __tablename__ = "event_registrations"
    __table_args__ = (UniqueConstraint("event_id", "student_id", name="uq_event_student"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    status: Mapped[RegistrationStatus] = mapped_column(String(16), index=True)
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    checked_in_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    event = relationship("Event", back_populates="registrations")
    student = relationship("User")
    ticket = relationship("Ticket", back_populates="registration", uselist=False, cascade="all, delete-orphan")


class WaitingListEntry(Base):
    __tablename__ = "waiting_list_entries"
    __table_args__ = (UniqueConstraint("event_id", "student_id", name="uq_waiting_event_student"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    position: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    event = relationship("Event", back_populates="waiting_list")
    student = relationship("User")


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    registration_id: Mapped[int] = mapped_column(ForeignKey("event_registrations.id"), unique=True, index=True)
    qr_payload: Mapped[str] = mapped_column(String(512), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    checked_in_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    registration = relationship("EventRegistration", back_populates="ticket")

