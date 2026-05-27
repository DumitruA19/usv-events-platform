from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.ai.chunking import chunk_text
from app.ai.cleaning import clean_text
from app.ai.db import exec_all, exec_one
from app.core.config import settings


class IngestionService:
    """
    Minimal ingestion skeleton backed by the Supabase schema in `supabase/schema.sql`.
    Safe default: only ingests mock content unless you extend fetchers.
    """

    def __init__(self, db: Session):
        self.db = db

    def register_source(self, *, name: str, kind: str = "mock", base_url: str | None = None, owner_user_id: str | None = None) -> dict:
        return exec_one(
            self.db,
            """
            insert into public.scraped_sources (name, kind, base_url, owner_user_id)
            values (:name, :kind, :base_url, :owner_user_id)
            returning id, name, kind, base_url, owner_user_id
            """,
            {"name": name, "kind": kind, "base_url": base_url, "owner_user_id": owner_user_id},
        ) or {}

    def run_mock_ingestion(self, *, requested_by: str | None = None) -> dict:
        """
        Creates a source + one page + chunks, tracking an ingestion job.

        Does not fetch external URLs. Extend with a real fetcher only when you can provide a safe target list.
        """
        max_pages = max(1, int(settings.scraper_max_pages))
        _ = max_pages
        started = datetime.now(timezone.utc)

        job = exec_one(
            self.db,
            """
            insert into public.ingestion_jobs (status, started_at, requested_by)
            values ('running', :started_at, :requested_by)
            returning id
            """,
            {"started_at": started.isoformat(), "requested_by": requested_by},
        )
        job_id = (job or {}).get("id")
        if not job_id:
            raise RuntimeError("Failed to create ingestion job (missing tables?)")

        source = self.register_source(name="Mock Source", kind="mock", base_url="mock://example", owner_user_id=requested_by)
        source_id = source.get("id")

        self._job_log(job_id, "info", "mock_ingestion_started", {"source_id": source_id})

        content = clean_text(
            """
            USV Events Platform knowledge base (mock).
            - Students can browse events and register.
            - Organizers create events and submit for approval.
            - Admins approve events and export reports.
            """
        )
        page = exec_one(
            self.db,
            """
            insert into public.scraped_pages (source_id, url, title, content_text, fetched_at)
            values (:source_id, :url, :title, :content_text, now())
            returning id
            """,
            {"source_id": source_id, "url": "mock://example/doc", "title": "Mock doc", "content_text": content},
        )
        page_id = (page or {}).get("id")

        chunks = chunk_text(content)
        for idx, c in enumerate(chunks):
            exec_one(
                self.db,
                """
                insert into public.kb_chunks (page_id, chunk_index, content, token_count, embedding_model)
                values (:page_id, :chunk_index, :content, null, null)
                returning id
                """,
                {"page_id": page_id, "chunk_index": idx, "content": c},
            )

        self._job_log(job_id, "info", "mock_ingestion_completed", {"chunks": len(chunks)})
        exec_one(
            self.db,
            """
            update public.ingestion_jobs
            set status='succeeded', finished_at=now(), stats = jsonb_build_object('pages', 1, 'chunks', :chunks)
            where id=:id
            returning id
            """,
            {"id": job_id, "chunks": len(chunks)},
        )
        return {"job_id": job_id, "pages": 1, "chunks": len(chunks)}

    def _job_log(self, job_id: str, level: str, message: str, context: dict) -> None:
        exec_one(
            self.db,
            """
            insert into public.ingestion_job_logs (job_id, level, message, context)
            values (:job_id, :level, :message, :context::jsonb)
            returning id
            """,
            {"job_id": job_id, "level": level, "message": message, "context": __import__("json").dumps(context)},
        )

    def list_jobs(self, *, limit: int = 50) -> list[dict]:
        limit = max(1, min(int(limit), 200))
        return exec_all(
            self.db,
            """
            select id, status, started_at, finished_at, stats, created_at
            from public.ingestion_jobs
            order by created_at desc
            limit :limit
            """,
            {"limit": limit},
        )

