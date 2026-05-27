from __future__ import annotations

import sys
import subprocess
from pathlib import Path
import runpy


def main() -> None:
    backend_dir = Path(__file__).resolve().parents[1]
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))

    # Ensure SQLite parent dir + storage folders exist before migrations.
    from app.core.database import init_storage_dirs

    init_storage_dirs()

    subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], cwd=str(backend_dir), check=True)

    # Seed after migrations.
    runpy.run_path(str(backend_dir / "scripts" / "seed.py"), run_name="__main__")


if __name__ == "__main__":
    main()
