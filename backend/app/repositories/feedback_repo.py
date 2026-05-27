from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.feedback import Feedback


class FeedbackRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_for_event(self, event_id: int) -> list[Feedback]:
        return list(self.db.scalars(select(Feedback).where(Feedback.event_id == event_id).order_by(Feedback.created_at.desc())))

    def stats_for_event(self, event_id: int) -> dict:
        avg_stmt = select(func.avg(Feedback.rating)).where(Feedback.event_id == event_id)
        cnt_stmt = select(func.count()).select_from(Feedback).where(Feedback.event_id == event_id)
        avg_rating = float(self.db.scalar(avg_stmt) or 0.0)
        count = int(self.db.scalar(cnt_stmt) or 0)
        return {"avg_rating": avg_rating, "count": count}

    def add(self, feedback: Feedback) -> Feedback:
        self.db.add(feedback)
        self.db.flush()
        return feedback

