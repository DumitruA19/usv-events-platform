from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user, require_roles
from app.core.database import get_db
from app.models.enums import RoleName
from app.schemas.notifications import NotificationOut
from app.services.notification_service import NotificationService

router = APIRouter()


@router.get("", response_model=list[NotificationOut])
def list_notifications(db: Session = Depends(get_db), user=Depends(get_current_user)):
    svc = NotificationService(db)
    items = svc.list_for_user(user)
    return items


@router.post("/mock-send-reminders")
def mock_send_reminders(db: Session = Depends(get_db), user=Depends(require_roles(RoleName.ADMIN))):
    # Production: disable mock reminder sender.
    from app.core.config import settings

    if settings.integrations_mode == "real":
        raise HTTPException(status_code=404, detail="Not found")
    svc = NotificationService(db)
    out = svc.mock_send_reminders(user)
    db.commit()
    return out

