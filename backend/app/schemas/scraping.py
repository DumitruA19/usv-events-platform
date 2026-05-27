from __future__ import annotations

from datetime import datetime

from app.schemas.base import ORMBaseModel

from app.models.enums import ScrapedDraftStatus


class ScrapedDraftOut(ORMBaseModel):
    id: int
    source: str
    status: ScrapedDraftStatus
    source_url: str | None
    image_url: str | None
    rejection_reason: str | None
    title: str
    description: str
    start_dt: datetime
    end_dt: datetime
    location_text: str | None
    category_text: str | None
