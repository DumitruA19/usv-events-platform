from __future__ import annotations

import os
import sys
from pathlib import Path

from sqlalchemy import select

# Allow running as `python scripts/reset_demo_passwords.py` from backend folder.
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.auth.password import hash_password  # noqa: E402
from app.core.config import settings  # noqa: E402
from app.core.database import SessionLocal  # noqa: E402
from app.models.enums import RoleName  # noqa: E402
from app.models.user import User  # noqa: E402


def _require_enabled() -> None:
    # Hard safety: only allow when explicitly enabled and not in production env.
    if settings.env.lower() in ("prod", "production"):
        raise SystemExit("Refusing to run in production ENV.")
    if os.getenv("DEMO_MODE", "").strip().lower() not in ("1", "true", "yes", "on"):
        raise SystemExit("Set DEMO_MODE=true to enable password reset.")


def _targets() -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for key in ("DEMO_ADMIN_IDENTIFIER", "DEMO_ORGANIZER_IDENTIFIER"):
        ident = os.getenv(key, "").strip()
        if ident:
            pw_key = "DEMO_ADMIN_PASSWORD" if "ADMIN" in key else "DEMO_ORGANIZER_PASSWORD"
            pw = os.getenv(pw_key, "").strip()
            if not pw:
                raise SystemExit(f"Missing {pw_key}.")
            out.append((ident, pw))
    return out


def main() -> None:
    _require_enabled()
    targets = _targets()
    if not targets:
        raise SystemExit("Nothing to do. Set DEMO_ADMIN_IDENTIFIER/DEMO_ORGANIZER_IDENTIFIER (+ passwords).")

    db = SessionLocal()
    try:
        for identifier, password in targets:
            raw = identifier.strip()
            user = db.scalar(select(User).where(User.username == raw)) or db.scalar(select(User).where(User.email == raw.lower()))
            if not user:
                raise SystemExit(f"User not found for identifier={identifier!r}")
            role = str(user.role.name).upper() if user.role else ""
            if role not in (RoleName.ADMIN.value, RoleName.ORGANIZER.value):
                raise SystemExit(f"Refusing to set password for role={role!r} (identifier={identifier!r}).")
            user.hashed_password = hash_password(password)
            user.is_active = True
            db.flush()
            print(f"Updated password for {identifier} (role={role}).")
        db.commit()
        print("Done.")
    finally:
        db.close()


if __name__ == "__main__":
    main()

