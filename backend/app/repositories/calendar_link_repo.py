from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.calendar_event_link import CalendarEventLink


class CalendarEventLinkRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_registration(self, registration_id: int) -> CalendarEventLink | None:
        return self.db.scalar(select(CalendarEventLink).where(CalendarEventLink.registration_id == registration_id))

    def create_link(self, *, registration_id: int, provider: str, calendar_id: str, provider_event_id: str) -> CalendarEventLink:
        link = CalendarEventLink(
            registration_id=registration_id,
            provider=provider,
            calendar_id=calendar_id,
            provider_event_id=provider_event_id,
        )
        self.db.add(link)
        self.db.flush()
        return link

    def delete_link(self, link: CalendarEventLink) -> None:
        self.db.delete(link)
        self.db.flush()

