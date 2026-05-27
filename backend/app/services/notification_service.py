from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.integrations.registry import get_integrations
from app.models.enums import RoleName
from app.models.event import Event
from app.models.system import Notification, Reminder
from app.repositories.event_repo import EventRepository
from app.utils.errors import forbidden


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class NotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.events = EventRepository(db)
        self.sender = get_integrations()["notification"]

    def list_for_user(self, user) -> list[Notification]:
        stmt = select(Notification).where(Notification.user_id == user.id).order_by(Notification.created_at.desc())
        return list(self.db.scalars(stmt))

    def mock_send_reminders(self, admin_or_system_user) -> dict:
        # For demo: send reminders for events starting within 48h to users with a reminder record.
        if admin_or_system_user.role.name != RoleName.ADMIN.value:
            raise forbidden("Admin only")
        now = utcnow()
        due = list(
            self.db.scalars(select(Reminder).where(Reminder.sent_at.is_(None), Reminder.scheduled_at <= now + timedelta(hours=48)))
        )
        sent = 0
        for r in due:
            ev = self.db.get(Event, r.event_id)
            if not ev:
                continue
            payload = {"event_id": ev.id, "title": ev.title, "start_dt": ev.start_dt.isoformat()}
            self.sender.send(r.user_id, "REMINDER", payload)
            self.db.add(Notification(user_id=r.user_id, type="REMINDER", payload_json=json.dumps(payload), created_at=now, sent_at=now))
            r.sent_at = now
            sent += 1
        self.db.flush()
        return {"sent": sent}

