from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.deps import require_roles
from app.core.database import get_db
from app.models.enums import RoleName
from app.schemas.feedback import FeedbackCreate, FeedbackOut, FeedbackStats
from app.services.feedback_service import FeedbackService

router = APIRouter()


@router.post("/{event_id}/feedback", response_model=FeedbackOut)
def create_feedback(
    event_id: int, payload: FeedbackCreate, db: Session = Depends(get_db), user=Depends(require_roles(RoleName.STUDENT))
):
    svc = FeedbackService(db)
    fb = svc.add(user, event_id, payload.rating, payload.comment)
    db.commit()
    return fb


@router.get("/{event_id}/feedback", response_model=list[FeedbackOut])
def list_feedback(event_id: int, db: Session = Depends(get_db)):
    svc = FeedbackService(db)
    return svc.list_for_event(event_id)


@router.get("/{event_id}/feedback/stats", response_model=FeedbackStats)
def stats(event_id: int, db: Session = Depends(get_db)):
    svc = FeedbackService(db)
    return svc.stats_for_event(event_id)

