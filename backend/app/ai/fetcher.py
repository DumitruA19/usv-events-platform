from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

import httpx

from app.core.config import settings


class UnsafeTargetError(ValueError):
    pass


def _allowed_hosts() -> set[str]:
    out: set[str] = set()
    for part in (settings.scrape_allowed_hosts or "").split(","):
        h = part.strip().lower()
        if h:
            out.add(h)
    return out


def fetch_text(target: str) -> str:
    """
    Safe-by-default fetcher.

    Supported targets:
    - mock://...    (returns deterministic placeholder content)
    - file://...    (reads a local file path)

    Intentionally NOT supported by default:
    - http(s)://... (real scraping). Add an allowlist + rate limiting before enabling.
    """
    t = (target or "").strip()
    if not t:
        raise ValueError("target is required")

    if t.startswith("mock://"):
        return f"Mock document for {t}\n\nReplace mock ingestion with a safe allowlisted fetcher."

    if t.startswith("file://"):
        raw = t[len("file://") :]
        p = Path(raw)
        if not p.exists() or not p.is_file():
            raise FileNotFoundError(raw)
        # Lowest-risk: only allow reading within the repo working directory.
        cwd = Path.cwd().resolve()
        rp = p.resolve()
        if cwd not in rp.parents and rp != cwd:
            raise UnsafeTargetError("Refusing to read files outside the working directory")
        return rp.read_text(encoding="utf-8")

    if t.startswith("http://") or t.startswith("https://"):
        if not settings.scrape_allow_http:
            raise UnsafeTargetError("HTTP scraping disabled (set SCRAPE_ALLOW_HTTP=true and SCRAPE_ALLOWED_HOSTS)")
        parsed = urlparse(t)
        host = (parsed.hostname or "").lower()
        allowed = _allowed_hosts()
        if not host or (allowed and host not in allowed):
            raise UnsafeTargetError("Host not allowlisted for scraping")
        headers = {"User-Agent": settings.scraper_user_agent}
        with httpx.Client(timeout=float(settings.scrape_timeout_seconds), headers=headers, follow_redirects=True) as client:
            res = client.get(t)
            res.raise_for_status()
            return res.text or ""

    raise UnsafeTargetError("Only mock://, file:// and allowlisted http(s):// targets are supported")

