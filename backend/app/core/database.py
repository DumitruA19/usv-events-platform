from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import normalized_database_url, settings


def _sqlite_connect_args(url: str) -> dict:
    if url.startswith("sqlite:"):
        return {"check_same_thread": False}
    return {}


def _ensure_sqlite_parent_dir() -> None:
    url = database_url
    if url.endswith(":memory:"):
        return
    prefixes = ("sqlite+pysqlite:///", "sqlite:///")
    if not url.startswith(prefixes):
        return
    raw_path = url.split(":///", 1)[1]
    # SQLAlchemy accepts forward slashes on Windows for absolute paths like C:/...
    db_path = Path(raw_path)
    if not db_path.is_absolute():
        db_path = Path.cwd() / db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)


def _build_engine(url: str):
    engine_kwargs = {
        "connect_args": _sqlite_connect_args(url),
    }

    # Supabase/Postgres connections can be dropped by the server or network layer.
    # Pre-ping lets SQLAlchemy refresh dead pooled connections before using them.
    if not url.startswith("sqlite:"):
        engine_kwargs.update(
            {
                "pool_pre_ping": True,
                "pool_recycle": 300,
                "pool_use_lifo": True,
            }
        )

    return create_engine(url, **engine_kwargs)


database_url = normalized_database_url()
engine = _build_engine(database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_storage_dirs() -> None:
    _ensure_sqlite_parent_dir()
    Path(settings.storage_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.storage_dir, "materials").mkdir(parents=True, exist_ok=True)
    Path(settings.storage_dir, "sponsor-logos").mkdir(parents=True, exist_ok=True)
    Path(settings.storage_dir, "reports").mkdir(parents=True, exist_ok=True)
