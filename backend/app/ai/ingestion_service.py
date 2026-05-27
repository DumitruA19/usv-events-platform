from __future__ import annotations

from datetime import datetime, timezone
import hashlib

from sqlalchemy.orm import Session

from app.ai.chunking import chunk_text
from app.ai.cleaning import clean_text
from app.ai.fetcher import fetch_text
from app.core.config import settings
from app.models.ai_kb import IngestionJob, IngestionJobLog, KBChunk, ScrapedPageKB, ScrapedSourceKB


class IngestionService:
    """
    Minimal ingestion skeleton backed by the Supabase schema in `supabase/schema.sql`.
    Safe default: only ingests mock content unless you extend fetchers.
    """

    def __init__(self, db: Session):
        self.db = db

    def register_source(self, *, name: str, kind: str = "mock", base_url: str | None = None, owner_user_id: int | None = None) -> dict:
        src = ScrapedSourceKB(
            owner_user_id=int(owner_user_id) if owner_user_id is not None else None,
            name=name,
            kind=kind,
            base_url=base_url,
            is_active=True,
        )
        self.db.add(src)
        self.db.flush()
        return {"id": src.id, "name": src.name, "kind": src.kind, "base_url": src.base_url, "owner_user_id": src.owner_user_id}

    def run_mock_ingestion(self, *, requested_by: int | None = None) -> dict:
        """
        Creates a source + one page + chunks, tracking an ingestion job.

        Does not fetch external URLs. Extend with a real fetcher only when you can provide a safe target list.
        """
        max_pages = max(1, int(settings.scraper_max_pages))
        _ = max_pages
        started = datetime.now(timezone.utc)

        job = IngestionJob(status="running", started_at=started, requested_by=int(requested_by) if requested_by is not None else None, stats={})
        self.db.add(job)
        self.db.flush()
        job_id = job.id

        source = self.register_source(name="Mock Source", kind="mock", base_url="mock://example", owner_user_id=requested_by)
        source_id = int(source.get("id"))

        self._job_log(job_id, "info", "mock_ingestion_started", {"source_id": source_id})

        content = clean_text(
            """
            USV Events Platform knowledge base (mock).
            - Students can browse events and register.
            - Organizers create events and submit for approval.
            - Admins approve events and export reports.
            """
        )
        page = ScrapedPageKB(source_id=source_id, url="mock://example/doc", title="Mock doc", content_text=content, content_hash=None, fetched_at=utcnow())
        self.db.add(page)
        self.db.flush()
        page_id = page.id

        chunks = chunk_text(content)
        for idx, c in enumerate(chunks):
            self.db.add(KBChunk(page_id=page_id, chunk_index=idx, content=c, token_count=None, embedding_model=None))

        self._job_log(job_id, "info", "mock_ingestion_completed", {"chunks": len(chunks)})
        job.status = "succeeded"
        job.finished_at = utcnow()
        job.stats = {"pages": 1, "chunks": len(chunks)}
        self.db.flush()
        return {"job_id": job_id, "pages": 1, "chunks": len(chunks)}

    def _job_log(self, job_id: str, level: str, message: str, context: dict) -> None:
        self.db.add(IngestionJobLog(job_id=int(job_id), level=level, message=message[:255], context=context))
        self.db.flush()

    def list_jobs(self, *, limit: int = 50) -> list[dict]:
        limit = max(1, min(int(limit), 200))
        rows = (
            self.db.query(IngestionJob)
            .order_by(IngestionJob.created_at.desc())
            .limit(limit)
            .all()
        )
        return [{"id": j.id, "status": j.status, "started_at": j.started_at, "finished_at": j.finished_at, "stats": j.stats, "created_at": j.created_at} for j in rows]

    def ingest_url(self, *, url: str, requested_by: int | None = None) -> dict:
        started = utcnow()
        job = IngestionJob(status="running", started_at=started, requested_by=int(requested_by) if requested_by is not None else None, stats={})
        self.db.add(job)
        self.db.flush()
        job_id = job.id

        try:
            self._job_log(str(job_id), "info", "fetch_start", {"url": url})
            raw = fetch_text(url)
            text = clean_text(raw)[: int(settings.scrape_max_text_chars)]
            if not text:
                raise ValueError("empty_content")
            h = hashlib.sha256(text.encode("utf-8")).hexdigest()

            src = ScrapedSourceKB(
                owner_user_id=int(requested_by) if requested_by is not None else None,
                name=url,
                base_url=url,
                kind="http",
                is_active=True,
            )
            self.db.add(src)
            self.db.flush()

            page = ScrapedPageKB(source_id=src.id, url=url, title=None, content_text=text, content_hash=h, fetched_at=utcnow())
            self.db.add(page)
            self.db.flush()

            chunks = chunk_text(text)
            for idx, c in enumerate(chunks):
                self.db.add(KBChunk(page_id=page.id, chunk_index=idx, content=c, token_count=None, embedding_model=None))
            self.db.flush()

            self._job_log(str(job_id), "info", "ingest_done", {"page_id": page.id, "chunks": len(chunks)})
            job.status = "succeeded"
            job.finished_at = utcnow()
            job.stats = {"pages": 1, "chunks": len(chunks)}
            self.db.flush()
            return {"job_id": job_id, "page_id": page.id, "chunks": len(chunks)}
        except Exception as e:
            self._job_log(str(job_id), "error", "ingest_failed", {"error": repr(e)})
            job.status = "failed"
            job.finished_at = utcnow()
            job.stats = {"error": repr(e)}
            self.db.flush()
            return {"job_id": job_id, "error": "failed", "detail": "Ingestion failed. Check logs."}

