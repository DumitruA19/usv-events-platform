from __future__ import annotations

from datetime import datetime

from app.schemas.base import ORMBaseModel


class NotificationOut(ORMBaseModel):
    id: int
    type: str
    payload_json: str
    created_at: datetime
