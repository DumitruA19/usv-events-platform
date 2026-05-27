from __future__ import annotations

from pathlib import Path


class UnsafeTargetError(ValueError):
    pass


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

    raise UnsafeTargetError("Only mock:// and file:// targets are allowed by default")

