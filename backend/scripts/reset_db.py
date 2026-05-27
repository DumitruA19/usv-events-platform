from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path


def _sqlite_file_path(backend_dir: Path) -> Path:
    # Mirror app/core/database.py parsing but keep this script self-contained.
    try:
        from app.core.config import settings
    except Exception:
        # Fallback to repo-local db
        return backend_dir / "data" / "app.db"

    url = settings.database_url
    if url.endswith(":memory:"):
        return backend_dir / "data" / "app.db"
    if ":///" not in url:
        return backend_dir / "data" / "app.db"
    raw_path = url.split(":///", 1)[1]
    p = Path(raw_path)
    if not p.is_absolute():
        p = backend_dir / p
    return p


def main() -> None:
    backend_dir = Path(__file__).resolve().parents[1]
    db_path = _sqlite_file_path(backend_dir)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    journal = Path(str(db_path) + "-journal")
    wal = Path(str(db_path) + "-wal")
    shm = Path(str(db_path) + "-shm")

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    if db_path.exists():
        backup = db_path.parent / f"{db_path.name}.bak-{ts}"
        shutil.move(str(db_path), str(backup))
        print(f"Moved {db_path} -> {backup}")
    else:
        print(f"No db found at {db_path}")

    for p in [journal, wal, shm]:
        if p.exists():
            p.unlink()
            print(f"Removed {p}")

    print("Done. Now run: python .\\scripts\\init_local.py")


if __name__ == "__main__":
    main()
