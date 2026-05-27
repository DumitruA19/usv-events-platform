from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.groq_client import GroqClient
from app.core.config import settings
from app.models.enums import RoleName, ScrapedDraftStatus
from app.models.enums import ParticipationMode
from app.models.scrape_source import ScrapeSource
from app.models.scraping import ScrapedEventDraft
from app.utils.errors import forbidden
from app.utils.rate_limit import RateLimiter


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


_host_rl = RateLimiter(capacity=3, refill_per_sec=0.5)  # ~30 req/min per host max


def _strip_html(html: str) -> str:
    html = re.sub(r"(?is)<(script|style)[^>]*>.*?</\\1>", " ", html)
    html = re.sub(r"(?is)<[^>]+>", " ", html)
    html = re.sub(r"\\s+", " ", html).strip()
    return html


def _guess_datetime(text: str) -> datetime | None:
    # Minimal heuristic: dd.mm.yyyy [hh:mm]
    m = re.search(r"(\\d{1,2})\\.(\\d{1,2})\\.(\\d{4})(?:\\s+(\\d{1,2}):(\\d{2}))?", text)
    if not m:
        return None
    day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
    hour = int(m.group(4) or 10)
    minute = int(m.group(5) or 0)
    try:
        return datetime(year, month, day, hour, minute, tzinfo=timezone.utc)
    except Exception:
        return None


@dataclass
class RunStats:
    created: int = 0
    duplicates: int = 0
    errors: int = 0


class AIScrapeService:
    def __init__(self, db: Session):
        self.db = db
        self.groq = GroqClient()

    def _ensure_admin(self, user) -> None:
        if user.role.name != RoleName.ADMIN.value:
            raise forbidden("Admin only")

    def add_source(self, admin_user, url: str) -> ScrapeSource:
        self._ensure_admin(admin_user)
        u = str(url).strip()
        existing = self.db.scalar(select(ScrapeSource).where(ScrapeSource.url == u))
        if existing:
            existing.is_active = True
            self.db.flush()
            return existing
        src = ScrapeSource(url=u, is_active=True, created_at=utcnow())
        self.db.add(src)
        self.db.flush()
        return src

    def list_sources(self, admin_user) -> list[ScrapeSource]:
        self._ensure_admin(admin_user)
        return list(self.db.scalars(select(ScrapeSource).order_by(ScrapeSource.created_at.desc())))

    def run(self, admin_user, *, url: str | None = None) -> RunStats:
        self._ensure_admin(admin_user)
        urls: list[str]
        if url:
            urls = [str(url)]
        else:
            urls = [s.url for s in self.list_sources(admin_user) if s.is_active]

        stats = RunStats()
        for u in urls:
            try:
                created, dup = self._scrape_one(u)
                stats.created += created
                stats.duplicates += dup
            except Exception:
                stats.errors += 1
        return stats

    def list_results(self, admin_user) -> list[ScrapedEventDraft]:
        self._ensure_admin(admin_user)
        return list(self.db.scalars(select(ScrapedEventDraft).order_by(ScrapedEventDraft.created_at.desc())))

    def approve(self, admin_user, draft_id: int) -> int:
        from app.services.scraping_service import ScrapingService

        self._ensure_admin(admin_user)
        svc = ScrapingService(self.db)
        e = svc.approve_draft(admin_user, draft_id)
        return e.id

    def reject(self, admin_user, draft_id: int) -> None:
        self._ensure_admin(admin_user)
        d = self.db.get(ScrapedEventDraft, draft_id)
        if not d:
            return
        if d.status == ScrapedDraftStatus.APPROVED.value:
            raise forbidden("Already approved")
        d.status = ScrapedDraftStatus.REJECTED.value
        if d.rejection_reason is None:
            d.rejection_reason = "Respins de administrator."
        self.db.flush()

    def _scrape_one(self, url: str) -> tuple[int, int]:
        parsed = urlparse(url)
        host = parsed.netloc.lower()
        if not host:
            raise ValueError("invalid url")
        if not _host_rl.allow(host):
            raise RuntimeError("rate_limited")

        text = self._fetch_clean_text(url)
        if not text:
            return (0, 0)

        # Deterministic single-event heuristic: use title + first date.
        title = self._guess_title(text) or parsed.netloc
        start = _guess_datetime(text)
        if title and start:
            end = start + timedelta(hours=2)
            created, dup = self._upsert_draft(
                source=host,
                payload={"sourceUrl": url, "title": title, "startDate": start.isoformat(), "endDate": end.isoformat()},
                title=title,
                description="",
                start_dt=start,
                end_dt=end,
                location=None,
                category=None,
                source_url=url,
                image_url=None,
            )
            return (created, dup)

        # Fallback: Groq extraction from cleaned text (limited).
        trimmed = text[: int(settings.scrape_max_text_chars)]
        system = (
            "Extrage evenimente universitare sau locale din text. "
            "Returneaza DOAR JSON valid, fara explicatii. "
            "Format: {\"items\": [{\"title\":\"...\",\"description\":\"...\",\"startDate\":\"...\",\"endDate\":\"...\",\"location\":\"...\",\"organizer\":\"...\",\"category\":\"...\",\"participationMode\":\"PHYSICAL|ONLINE|HYBRID\",\"sourceUrl\":\"...\"}]} "
            "Daca nu exista evenimente, returneaza {\"items\": []}."
        )
        user = f"Sursa: {url}\n\nText:\n{trimmed}"
        res = self.groq.chat_json(system=system, user=user)
        if res.status != "ok":
            return (0, 0)
        data = json.loads(res.content)
        items = data.get("items") if isinstance(data, dict) else None
        if not isinstance(items, list):
            return (0, 0)

        created = 0
        dup = 0
        for it in items[:10]:
            try:
                t = str(it.get("title") or "").strip()[:255]
                if not t:
                    continue
                start_s = str(it.get("startDate") or "").strip()
                end_s = str(it.get("endDate") or "").strip()
                start_dt = datetime.fromisoformat(start_s.replace("Z", "+00:00")) if start_s else None
                end_dt = datetime.fromisoformat(end_s.replace("Z", "+00:00")) if end_s else None
                if not start_dt:
                    continue
                if not end_dt:
                    end_dt = start_dt + timedelta(hours=2)
                c, d = self._upsert_draft(
                    source=host,
                    payload=it,
                    title=t,
                    description=str(it.get("description") or "")[:10000],
                    start_dt=start_dt,
                    end_dt=end_dt,
                    location=str(it.get("location") or "")[:255] or None,
                    category=str(it.get("category") or "")[:255] or None,
                    source_url=str(it.get("sourceUrl") or url)[:1024] or url,
                    image_url=str(it.get("imageUrl") or "")[:1024] or None,
                )
                created += c
                dup += d
            except Exception:
                continue
        return (created, dup)

    def _fetch_clean_text(self, url: str) -> str:
        headers = {"User-Agent": settings.scraper_user_agent}
        with httpx.Client(timeout=float(settings.scrape_timeout_seconds), headers=headers, follow_redirects=True) as client:
            # Best-effort robots.txt respect (minimal).
            try:
                parsed = urlparse(url)
                robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
                r = client.get(robots_url)
                if r.status_code == 200 and "Disallow:" in r.text:
                    path = parsed.path or "/"
                    for line in r.text.splitlines():
                        line = line.strip()
                        if not line.lower().startswith("disallow:"):
                            continue
                        dis = line.split(":", 1)[1].strip()
                        if dis and path.startswith(dis):
                            return ""
            except Exception:
                pass

            res = client.get(url)
            res.raise_for_status()
            html = res.text or ""
        return _strip_html(html)

    def _guess_title(self, text: str) -> str | None:
        if not text:
            return None
        # First chunk up to punctuation or 80 chars.
        first = re.split(r"[\\.!?\\n\\r]", text, maxsplit=1)[0].strip()
        if not first:
            return None
        return first[:80]

    def _upsert_draft(
        self,
        *,
        source: str,
        payload: dict,
        title: str,
        description: str,
        start_dt: datetime,
        end_dt: datetime,
        location: str | None,
        category: str | None,
        source_url: str | None,
        image_url: str | None,
    ) -> tuple[int, int]:
        # Dedup: same title + start_dt + source_url (preferred), fallback to source host.
        start_key = start_dt.replace(second=0, microsecond=0)
        stmt = select(ScrapedEventDraft).where(
            ScrapedEventDraft.title == title,
            ScrapedEventDraft.start_dt == start_key,
        )
        if source_url:
            stmt = stmt.where(ScrapedEventDraft.source_url == source_url)
        else:
            stmt = stmt.where(ScrapedEventDraft.source == source)
        existing = self.db.scalar(stmt)
        if existing:
            if existing.status == ScrapedDraftStatus.PENDING.value:
                existing.raw_payload_json = json.dumps(payload, ensure_ascii=True)
                existing.image_url = image_url or existing.image_url
                self.db.flush()
            return (0, 1)

        d = ScrapedEventDraft(
            source=source,
            status=ScrapedDraftStatus.PENDING.value,
            source_url=source_url,
            image_url=image_url,
            raw_payload_json=json.dumps(payload, ensure_ascii=True),
            title=title,
            description=description or "",
            start_dt=start_key,
            end_dt=end_dt,
            location_text=location,
            category_text=category,
            created_at=utcnow(),
        )
        self.db.add(d)
        self.db.flush()
        return (1, 0)
