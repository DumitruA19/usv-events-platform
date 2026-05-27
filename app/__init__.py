from __future__ import annotations

from pathlib import Path

# Allow `uvicorn app.main:app` to work both from `backend/` and repo root by
# exposing `backend/app` as the package search location for `app.*` modules.
_backend_app_dir = Path(__file__).resolve().parents[1] / "backend" / "app"
__path__ = [str(_backend_app_dir)]
