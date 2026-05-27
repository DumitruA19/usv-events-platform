from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import EventStatus, ParticipationMode


class EventCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    description: str = Field(default="", max_length=10000)
    start_dt: datetime
    end_dt: datetime
    category_id: int | None = None
    faculty_department_id: int | None = None
    location_id: int | None = None
    participation_mode: ParticipationMode = ParticipationMode.PHYSICAL
    registration_link: str | None = Field(default=None, max_length=512)
    free_entry: bool = True
    requires_registration: bool = False
    requires_ticket: bool = False
    capacity: int | None = Field(default=None, ge=1)
    registration_deadline: datetime | None = None
    has_qr_code: bool = False
    max_material_files: int = Field(default=10, ge=0, le=50)
    max_material_mb: int = Field(default=20, ge=1, le=200)


class EventUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=255)
    description: str | None = Field(default=None, max_length=10000)
    start_dt: datetime | None = None
    end_dt: datetime | None = None
    category_id: int | None = None
    faculty_department_id: int | None = None
    location_id: int | None = None
    participation_mode: ParticipationMode | None = None
    registration_link: str | None = Field(default=None, max_length=512)
    free_entry: bool | None = None
    requires_registration: bool | None = None
    requires_ticket: bool | None = None
    capacity: int | None = Field(default=None, ge=1)
    registration_deadline: datetime | None = None
    has_qr_code: bool | None = None
    max_material_files: int | None = Field(default=None, ge=0, le=50)
    max_material_mb: int | None = Field(default=None, ge=1, le=200)


class EventListItem(BaseModel):
    id: int
    title: str
    start_dt: datetime
    end_dt: datetime
    location_name: str | None
    category_name: str | None
    organizer_name: str | None
    status: EventStatus
    participation_mode: ParticipationMode
    free_entry: bool
    requires_registration: bool
    has_qr_code: bool


class SponsorOut(BaseModel):
    name: str
    logo_path: str | None = None


class MaterialOut(BaseModel):
    id: int
    filename: str
    size_bytes: int


class EventOut(BaseModel):
    id: int
    title: str
    description: str
    start_dt: datetime
    end_dt: datetime
    location_name: str | None
    category_name: str | None
    organizer_name: str | None
    status: EventStatus
    participation_mode: ParticipationMode
    registration_link: str | None
    free_entry: bool
    requires_registration: bool
    requires_ticket: bool
    capacity: int | None
    has_qr_code: bool
    sponsors: list[SponsorOut] = []
    materials: list[MaterialOut] = []


class PagedEvents(BaseModel):
    items: list[EventListItem]
    total: int


class CalendarEvents(BaseModel):
    items: list[EventListItem]

