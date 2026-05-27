from __future__ import annotations

from datetime import datetime

from pydantic import Field

from app.schemas.base import ORMBaseModel


class FeedbackCreate(ORMBaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=5000)


class FeedbackOut(ORMBaseModel):
    id: int
    student_id: int
    rating: int
    comment: str | None
    sentiment_label: str | None
    created_at: datetime


class FeedbackStats(ORMBaseModel):
    avg_rating: float
    count: int
    sentiment_summary: dict[str, int]
