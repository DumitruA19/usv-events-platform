from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session


def dialect_name(db: Session) -> str:
    return str(db.bind.dialect.name) if db.bind is not None else "unknown"


def exec_one(db: Session, stmt: str, params: dict) -> dict | None:
    res = db.execute(text(stmt), params)
    row = res.mappings().first()
    return dict(row) if row else None


def exec_all(db: Session, stmt: str, params: dict) -> list[dict]:
    res = db.execute(text(stmt), params)
    return [dict(r) for r in res.mappings().all()]

