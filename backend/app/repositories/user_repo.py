from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_username(self, username: str) -> User | None:
        return self.db.scalar(select(User).where(User.username == username))

    def get_by_email(self, email: str) -> User | None:
        raw = (email or "").strip().lower()
        if not raw:
            return None
        # Be tolerant to case differences in stored emails.
        return self.db.scalar(select(User).where(func.lower(User.email) == raw))

    def list_users(self) -> list[User]:
        return list(self.db.scalars(select(User).order_by(User.id)))

    def add(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        return user

