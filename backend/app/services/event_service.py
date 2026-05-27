from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.integrations.registry import get_integrations
from app.models.enums import EventStatus, RoleName
from app.models.event import Event
from app.repositories.event_repo import EventRepository
from app.utils.errors import bad_request, forbidden, not_found
from app.utils.ics import build_ics_event


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class EventService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = EventRepository(db)

    def get(self, event_id: int) -> Event:
        e = self.repo.get(event_id)
        if not e:
            raise not_found("Event not found")
        return e

    def list_public(self, **kwargs) -> list[Event]:
        # Public listing shows APPROVED/PUBLISHED by default.
        statuses = kwargs.pop("statuses", None)
        if statuses is None:
            statuses = [EventStatus.PUBLISHED, EventStatus.APPROVED]
        return self.repo.list(statuses=statuses, **kwargs)

    def list_any(self, **kwargs) -> list[Event]:
        return self.repo.list(**kwargs)

    def create(self, organizer_user, data) -> Event:
        if organizer_user.role.name != RoleName.ORGANIZER.value:
            raise forbidden("Only organizers can create events")
        if data.end_dt <= data.start_dt:
            raise bad_request("end_dt must be after start_dt")
        e = Event(
            title=data.title,
            description=data.description,
            start_dt=data.start_dt,
            end_dt=data.end_dt,
            category_id=data.category_id,
            faculty_department_id=data.faculty_department_id,
            location_id=data.location_id,
            participation_mode=data.participation_mode.value,
            organizer_id=organizer_user.id,
            registration_link=data.registration_link,
            free_entry=data.free_entry,
            requires_registration=data.requires_registration,
            requires_ticket=data.requires_ticket,
            capacity=data.capacity,
            registration_deadline=data.registration_deadline,
            has_qr_code=data.has_qr_code,
            max_material_files=data.max_material_files,
            max_material_mb=data.max_material_mb,
            status=EventStatus.DRAFT.value,
            created_at=utcnow(),
            updated_at=utcnow(),
        )
        self.repo.add(e)
        return e

    def update(self, user, event_id: int, data) -> Event:
        e = self.get(event_id)
        if user.role.name == RoleName.ORGANIZER.value and e.organizer_id != user.id:
            raise forbidden("Organizers can manage only their own events")
        if user.role.name not in [RoleName.ORGANIZER.value, RoleName.ADMIN.value]:
            raise forbidden("Not allowed")

        for field, value in data.model_dump(exclude_unset=True).items():
            if value is None:
                setattr(e, field, None)
            else:
                if field == "participation_mode":
                    setattr(e, field, value.value)
                else:
                    setattr(e, field, value)

        if e.end_dt <= e.start_dt:
            raise bad_request("end_dt must be after start_dt")
        e.updated_at = utcnow()
        self.db.flush()
        return e

    def delete(self, user, event_id: int) -> None:
        e = self.get(event_id)
        if user.role.name == RoleName.ORGANIZER.value and e.organizer_id != user.id:
            raise forbidden("Organizers can delete only their own events")
        if user.role.name not in [RoleName.ORGANIZER.value, RoleName.ADMIN.value]:
            raise forbidden("Not allowed")
        self.repo.delete(e)

    def submit_for_approval(self, organizer_user, event_id: int) -> Event:
        e = self.get(event_id)
        if organizer_user.role.name != RoleName.ORGANIZER.value or e.organizer_id != organizer_user.id:
            raise forbidden("Only the owning organizer can submit")
        if e.status not in [EventStatus.DRAFT.value, EventStatus.REJECTED.value]:
            raise bad_request("Event is not in a submittable state")
        e.status = EventStatus.PENDING_APPROVAL.value
        e.updated_at = utcnow()
        self.db.flush()
        return e

    def approve(self, admin_user, event_id: int) -> Event:
        e = self.get(event_id)
        if admin_user.role.name != RoleName.ADMIN.value:
            raise forbidden("Admin only")
        if e.status != EventStatus.PENDING_APPROVAL.value:
            raise bad_request("Event is not pending approval")
        e.status = EventStatus.PUBLISHED.value
        e.updated_at = utcnow()
        self.db.flush()
        return e

    def reject(self, admin_user, event_id: int) -> Event:
        e = self.get(event_id)
        if admin_user.role.name != RoleName.ADMIN.value:
            raise forbidden("Admin only")
        if e.status != EventStatus.PENDING_APPROVAL.value:
            raise bad_request("Event is not pending approval")
        e.status = EventStatus.REJECTED.value
        e.updated_at = utcnow()
        self.db.flush()
        return e

    def export_ics(self, event_id: int) -> str:
        e = self.get(event_id)
        loc = e.location.name if e.location else None
        return build_ics_event(
            uid=f"usv-events-{e.id}@local",
            title=e.title,
            description=e.description,
            start_dt=e.start_dt,
            end_dt=e.end_dt,
            location=loc,
        )

    def mock_google_calendar(self, user, event_id: int) -> dict:
        e = self.get(event_id)
        integ = get_integrations()["google_calendar"]
        payload = integ.mock_add_event(user.id, e.id, e.title, e.start_dt, e.end_dt)
        # Also store notification for demo traceability.
        from app.models.system import Notification

        n = Notification(user_id=user.id, type="MOCK_GOOGLE_CALENDAR", payload_json=json.dumps(payload))
        self.db.add(n)
        self.db.flush()
        return payload

