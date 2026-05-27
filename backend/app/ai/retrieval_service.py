from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.ai.db import dialect_name, exec_all


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

        dialect = dialect_name(self.db)
        if dialect == "sqlite":
            rows = exec_all(
                self.db,
                """
                select id, content
                from kb_chunks
                where content like :like
                order by updated_at desc
                limit :limit
                """,
                {"like": f"%{q}%", "limit": limit},
            )
        else:
            rows = exec_all(
                self.db,
                """
                select id, content
                from public.kb_chunks
                where content ilike :like
                order by updated_at desc
                limit :limit
                """,
                {"like": f"%{q}%", "limit": limit},
            )

        return [RetrievedChunk(id=str(r["id"]), content=str(r["content"]), score=None) for r in rows]

