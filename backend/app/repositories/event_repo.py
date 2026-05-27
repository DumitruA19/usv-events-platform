from __future__ import annotations

from datetime import datetime

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.enums import EventStatus, ParticipationMode
from app.models.event import Event, EventSponsor


class EventRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, event_id: int) -> Event | None:
        stmt = (
            select(Event)
            .where(Event.id == event_id)
            .options(
                joinedload(Event.location),
                joinedload(Event.category),
                joinedload(Event.organizer),
                joinedload(Event.materials),
                joinedload(Event.sponsors).joinedload(EventSponsor.sponsor),
            )
        )
        return self.db.scalar(stmt)

    def list(
        self,
        *,
        q: str | None,
        date_from: datetime | None,
        date_to: datetime | None,
        category_id: int | None,
        organizer_id: int | None,
        location_id: int | None,
        faculty_department_id: int | None,
        participation_mode: ParticipationMode | None,
        free_entry: bool | None,
        requires_registration: bool | None,
        has_qr_code: bool | None,
        filter_operator: str,
        statuses: list[EventStatus] | None,
        sort_by: str,
        sort_dir: str,
    ) -> list[Event]:
        conditions = []
        if q:
            conditions.append(Event.title.ilike(f"%{q}%"))
        if date_from:
            conditions.append(Event.start_dt >= date_from)
        if date_to:
            conditions.append(Event.start_dt <= date_to)
        if category_id:
            conditions.append(Event.category_id == category_id)
        if organizer_id:
            conditions.append(Event.organizer_id == organizer_id)
        if location_id:
            conditions.append(Event.location_id == location_id)
        if faculty_department_id:
            conditions.append(Event.faculty_department_id == faculty_department_id)
        if participation_mode:
            conditions.append(Event.participation_mode == participation_mode.value)
        if free_entry is not None:
            conditions.append(Event.free_entry == free_entry)
        if requires_registration is not None:
            conditions.append(Event.requires_registration == requires_registration)
        if has_qr_code is not None:
            conditions.append(Event.has_qr_code == has_qr_code)
        if statuses:
            conditions.append(Event.status.in_([s.value for s in statuses]))

        stmt = select(Event).options(joinedload(Event.location), joinedload(Event.category), joinedload(Event.organizer))
        if conditions:
            op = (filter_operator or "AND").upper()
            if op == "OR":
                stmt = stmt.where(or_(*conditions))
            else:
                stmt = stmt.where(and_(*conditions))

        if sort_by == "title":
            order_col = Event.title
        elif sort_by == "category":
            order_col = Event.category_id
        elif sort_by == "organizer":
            order_col = Event.organizer_id
        else:
            order_col = Event.start_dt

        if (sort_dir or "asc").lower() == "desc":
            stmt = stmt.order_by(order_col.desc())
        else:
            stmt = stmt.order_by(order_col.asc())

        return list(self.db.scalars(stmt))

    def add(self, event: Event) -> Event:
        self.db.add(event)
        self.db.flush()
        return event

    def delete(self, event: Event) -> None:
        self.db.delete(event)
