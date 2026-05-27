from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import EventStatus, RegistrationStatus, RoleName
from app.models.event import Event
from app.models.registration import EventRegistration
from app.utils.errors import forbidden


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class StudentService:
    def __init__(self, db: Session):
        self.db = db

    def my_registrations(self, student_user) -> list[dict]:
        if student_user.role.name != RoleName.STUDENT.value:
            raise forbidden("Students only")
        stmt = (
            select(EventRegistration, Event)
            .join(Event, EventRegistration.event_id == Event.id)
            .where(EventRegistration.student_id == student_user.id, EventRegistration.status != RegistrationStatus.CANCELLED.value)
            .order_by(Event.start_dt.asc())
        )
        rows = self.db.execute(stmt).all()
        items = []
        for reg, ev in rows:
            items.append(
                {
                    "event_id": ev.id,
                    "title": ev.title,
                    "start_dt": ev.start_dt,
                    "status": reg.status,
                    "ticket_qr_payload": reg.ticket.qr_payload if reg.ticket else None,
                }
            )
        return items

    def recommendations(self, student_user, max_items: int = 5) -> list[dict]:
        if student_user.role.name != RoleName.STUDENT.value:
            raise forbidden("Students only")
        now = utcnow()

        regs = list(
            self.db.scalars(
                select(EventRegistration).where(
                    EventRegistration.student_id == student_user.id,
                    EventRegistration.status.in_([RegistrationStatus.REGISTERED.value, RegistrationStatus.CHECKED_IN.value]),
                )
            )
        )
        registered_event_ids = {r.event_id for r in regs}

        cat_ids = set()
        if registered_event_ids:
            for ev in self.db.scalars(select(Event).where(Event.id.in_(registered_event_ids))):
                if ev.category_id:
                    cat_ids.add(ev.category_id)

        # Candidate upcoming published events.
        stmt = select(Event).where(Event.status.in_([EventStatus.PUBLISHED.value, EventStatus.APPROVED.value]), Event.start_dt >= now)
        if cat_ids:
            stmt = stmt.where(Event.category_id.in_(cat_ids))
        stmt = stmt.order_by(Event.start_dt.asc()).limit(30)
        candidates = [e for e in self.db.scalars(stmt) if e.id not in registered_event_ids]

        items = []
        for ev in candidates[:max_items]:
            items.append({"event_id": ev.id, "title": ev.title, "start_dt": ev.start_dt, "reason": "Based on your registrations"})
        if len(items) < max_items:
            fallback = list(
                self.db.scalars(
                    select(Event)
                    .where(Event.status.in_([EventStatus.PUBLISHED.value, EventStatus.APPROVED.value]), Event.start_dt >= now)
                    .order_by(Event.start_dt.asc())
                    .limit(30)
                )
            )
            for ev in fallback:
                if ev.id in registered_event_ids:
                    continue
                if any(i["event_id"] == ev.id for i in items):
                    continue
                items.append({"event_id": ev.id, "title": ev.title, "start_dt": ev.start_dt, "reason": "Upcoming event"})
                if len(items) >= max_items:
                    break
        return items

