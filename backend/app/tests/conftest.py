from __future__ import annotations

import shutil
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.database import get_db
from app.integrations.registry import get_integrations
from app.main import create_app
from app.models.base import Base

import app.models  # noqa: F401


@pytest.fixture()
def temp_storage_dir():
    # Keep temp files inside the repo (sandbox/write permissions).
    backend_dir = Path(__file__).resolve().parents[2]
    tmp_root = backend_dir / ".tmp-tests"
    tmp_root.mkdir(parents=True, exist_ok=True)

    d = tmp_root / f"run-{uuid.uuid4().hex}"
    d.mkdir(parents=True, exist_ok=True)
    try:
        yield str(d)
    finally:
        shutil.rmtree(d, ignore_errors=True)


@pytest.fixture()
def db_session(temp_storage_dir):
    settings.database_url = "sqlite+pysqlite:///:memory:"
    settings.jwt_secret_key = "test-secret"
    settings.storage_dir = str(Path(temp_storage_dir) / "storage")
    settings.integrations_mode = "mock"
    get_integrations.cache_clear()

    # In-memory SQLite needs StaticPool so the same DB is shared across threads
    # (TestClient serves requests in a different thread).
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(db_session):
    app = create_app()

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)
