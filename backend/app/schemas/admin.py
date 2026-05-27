from __future__ import annotations

from pydantic import BaseModel, Field


class OrganizerCreate(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=8, max_length=128)
    display_name: str | None = Field(default=None, max_length=255)
    faculty_department_id: int | None = None


class OrganizerUpdate(BaseModel):
    password: str | None = Field(default=None, min_length=8, max_length=128)
    is_active: bool | None = None
    display_name: str | None = Field(default=None, max_length=255)
    faculty_department_id: int | None = None


class UserOut(BaseModel):
    id: int
    email: str | None
    username: str | None
    role: str
    is_active: bool


class UserUpdate(BaseModel):
    role: str | None = Field(default=None, max_length=32)
    is_active: bool | None = None


class EventRejectRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=2000)


class EventCancelRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=2000)

