from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.password import hash_password
from app.models.enums import RoleName
from app.models.role import Role
from app.models.user import User


def seed_roles(db: Session):
    for name in [RoleName.ADMIN.value, RoleName.ORGANIZER.value, RoleName.STUDENT.value]:
        if not db.scalar(select(Role).where(Role.name == name)):
            db.add(Role(name=name))
    db.flush()


def create_user(db: Session, role: str, username: str | None, email: str | None, password: str | None) -> User:
    r = db.scalar(select(Role).where(Role.name == role))
    assert r
    u = User(username=username, email=email, hashed_password=hash_password(password) if password else None, role_id=r.id, is_active=True)
    db.add(u)
    db.flush()
    return u


def login(client, username: str, password: str) -> str:
    res = client.post("/auth/login", json={"username": username, "password": password})
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


def mock_student_login(client, email: str) -> str:
    res = client.post("/auth/mock-google-login", json={"email": email})
    assert res.status_code == 200, res.text
    return res.json()["access_token"]

