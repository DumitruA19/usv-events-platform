from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import EventStatus, ParticipationMode


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str] = mapped_column(Text, default="")

    start_dt: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    end_dt: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    status: Mapped[EventStatus] = mapped_column(String(32), index=True, default=EventStatus.DRAFT)
    participation_mode: Mapped[ParticipationMode] = mapped_column(String(16), default=ParticipationMode.PHYSICAL)

    organizer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("event_categories.id"), nullable=True)
    faculty_department_id: Mapped[int | None] = mapped_column(ForeignKey("faculty_departments.id"), nullable=True)
    location_id: Mapped[int | None] = mapped_column(ForeignKey("locations.id"), nullable=True)

    registration_link: Mapped[str | None] = mapped_column(String(512), nullable=True)
    free_entry: Mapped[bool] = mapped_column(Boolean, default=True)
    requires_registration: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_ticket: Mapped[bool] = mapped_column(Boolean, default=False)
    has_qr_code: Mapped[bool] = mapped_column(Boolean, default=False)

    capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    registration_deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    max_material_files: Mapped[int] = mapped_column(Integer, default=10)
    max_material_mb: Mapped[int] = mapped_column(Integer, default=20)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    # Admin moderation metadata (optional).
    moderated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    moderated_by_admin_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    cancel_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    organizer = relationship("User", back_populates="organized_events", foreign_keys=[organizer_id])
    category = relationship("EventCategory")
    faculty_department = relationship("FacultyDepartment")
    location = relationship("Location")

    sponsors = relationship("EventSponsor", back_populates="event", cascade="all, delete-orphan")
    materials = relationship("EventMaterial", back_populates="event", cascade="all, delete-orphan")

    registrations = relationship("EventRegistration", back_populates="event", cascade="all, delete-orphan")
    waiting_list = relationship("WaitingListEntry", back_populates="event", cascade="all, delete-orphan")
    feedback = relationship("Feedback", back_populates="event", cascade="all, delete-orphan")


class Sponsor(Base):
    __tablename__ = "sponsors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    logo_path: Mapped[str | None] = mapped_column(String(512), nullable=True)

    events = relationship("EventSponsor", back_populates="sponsor")


class EventSponsor(Base):
    __tablename__ = "event_sponsors"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), index=True)
    sponsor_id: Mapped[int] = mapped_column(ForeignKey("sponsors.id"), index=True)
    tier: Mapped[str | None] = mapped_column(String(64), nullable=True)

    event = relationship("Event", back_populates="sponsors")
    sponsor = relationship("Sponsor", back_populates="events")


class EventMaterial(Base):
    __tablename__ = "event_materials"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), index=True)
    filename: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(128))
    size_bytes: Mapped[int] = mapped_column(Integer)
    stored_path: Mapped[str] = mapped_column(String(512))
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    event = relationship("Event", back_populates="materials")

