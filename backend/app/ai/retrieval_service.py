from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.ai_kb import KBChunk


@dataclass(frozen=True)
class RetrievedChunk:
    id: str
    content: str
    score: float | None


class RetrievalService:
    def __init__(self, db: Session):
        self.db = db

    def search_chunks(self, query: str, *, limit: int = 6) -> list[RetrievedChunk]:
        q = (query or "").strip()
        if not q:
            return []
        limit = max(1, min(int(limit), 20))

        # Demo-safe: if KB table/schema isn't ready, treat KB as empty instead of 500.
        try:
            like = f"%{q.lower()}%"
            stmt = (
                select(KBChunk.id, KBChunk.content)
                .where(func.lower(KBChunk.content).like(like))
                .order_by(KBChunk.updated_at.desc())
                .limit(limit)
            )
            rows = list(self.db.execute(stmt).all())
            return [RetrievedChunk(id=str(r[0]), content=str(r[1]), score=None) for r in rows]
        except Exception:
            return []

