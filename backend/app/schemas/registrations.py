from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.models.enums import RegistrationStatus


class RegisterResponse(BaseModel):
    status: RegistrationStatus
    message: str
    ticket_qr_payload: str | None = None


class ParticipantOut(BaseModel):
    student_id: int
    email: str | None
    status: RegistrationStatus
    registered_at: datetime
    ticket_qr_payload: str | None = None


class WaitingOut(BaseModel):
    student_id: int
    email: str | None
    position: int
    created_at: datetime


class CheckInRequest(BaseModel):
    qr_payload: str


class CheckInResponse(BaseModel):
    status: RegistrationStatus
    message: str

