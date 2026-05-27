from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.integrations.registry import get_integrations
from app.models.enums import RoleName
from app.models.feedback import Feedback
from app.repositories.event_repo import EventRepository
from app.repositories.feedback_repo import FeedbackRepository
from app.utils.errors import bad_request, forbidden, not_found


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class FeedbackService:
    def __init__(self, db: Session):
        self.db = db
        self.events = EventRepository(db)
        self.repo = FeedbackRepository(db)
        self.sentiment = get_integrations()["sentiment"]

    def add(self, student_user, event_id: int, rating: int, comment: str | None) -> Feedback:
        if student_user.role.name != RoleName.STUDENT.value:
            raise forbidden("Students only")
        e = self.events.get(event_id)
        if not e:
            raise not_found("Event not found")
        # SQLite often returns naive datetimes even when timezone=True; normalize to UTC-aware.
        end_dt = e.end_dt
        if end_dt.tzinfo is None:
            end_dt = end_dt.replace(tzinfo=timezone.utc)
        if utcnow() <= end_dt:
            raise bad_request("Feedback is allowed only after the event ends")
        label = self.sentiment.analyze(comment)
        fb = Feedback(event_id=event_id, student_id=student_user.id, rating=rating, comment=comment, sentiment_label=label, created_at=utcnow())
        self.repo.add(fb)
        return fb

    def list_for_event(self, event_id: int) -> list[Feedback]:
        e = self.events.get(event_id)
        if not e:
            raise not_found("Event not found")
        return self.repo.list_for_event(event_id)

    def stats_for_event(self, event_id: int) -> dict:
        items = self.list_for_event(event_id)
        base = self.repo.stats_for_event(event_id)
        sentiments = Counter([i.sentiment_label or "NEUTRAL" for i in items])
        base["sentiment_summary"] = dict(sentiments)
        return base
