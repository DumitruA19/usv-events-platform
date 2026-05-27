from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.registration import EventRegistration, Ticket, WaitingListEntry


class RegistrationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_registration(self, event_id: int, student_id: int) -> EventRegistration | None:
        stmt = (
            select(EventRegistration)
            .where(EventRegistration.event_id == event_id, EventRegistration.student_id == student_id)
            .options(joinedload(EventRegistration.ticket))
        )
        return self.db.scalar(stmt)

    def count_registered(self, event_id: int) -> int:
        stmt = select(func.count()).select_from(EventRegistration).where(
            EventRegistration.event_id == event_id, EventRegistration.status == "REGISTERED"
        )
        return int(self.db.scalar(stmt) or 0)

    def list_participants(self, event_id: int) -> list[EventRegistration]:
        stmt = (
            select(EventRegistration)
            .where(EventRegistration.event_id == event_id, EventRegistration.status.in_(["REGISTERED", "CHECKED_IN"]))
            .options(joinedload(EventRegistration.student), joinedload(EventRegistration.ticket))
            .order_by(EventRegistration.registered_at.asc())
        )
        return list(self.db.scalars(stmt))

    def list_waiting(self, event_id: int) -> list[WaitingListEntry]:
        stmt = (
            select(WaitingListEntry)
            .where(WaitingListEntry.event_id == event_id)
            .options(joinedload(WaitingListEntry.student))
            .order_by(WaitingListEntry.position.asc())
        )
        return list(self.db.scalars(stmt))

    def next_waiting_position(self, event_id: int) -> int:
        stmt = select(func.max(WaitingListEntry.position)).where(WaitingListEntry.event_id == event_id)
        max_pos = self.db.scalar(stmt)
        return int(max_pos or 0) + 1

    def add_registration(self, reg: EventRegistration) -> EventRegistration:
        self.db.add(reg)
        self.db.flush()
        return reg

    def add_waiting(self, entry: WaitingListEntry) -> WaitingListEntry:
        self.db.add(entry)
        self.db.flush()
        return entry

    def remove_waiting(self, entry: WaitingListEntry) -> None:
        self.db.delete(entry)

    def add_ticket(self, ticket: Ticket) -> Ticket:
        self.db.add(ticket)
        self.db.flush()
        return ticket

    def find_ticket(self, qr_payload: str) -> Ticket | None:
        return self.db.scalar(select(Ticket).where(Ticket.qr_payload == qr_payload).options(joinedload(Ticket.registration)))

