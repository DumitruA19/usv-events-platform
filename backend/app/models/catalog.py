from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class EventCategory(Base):
    __tablename__ = "event_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, index=True)


class FacultyDepartment(Base):
    __tablename__ = "faculty_departments"

    id: Mapped[int] = mapped_column(primary_key=True)
    faculty: Mapped[str] = mapped_column(String(255), index=True)
    department: Mapped[str] = mapped_column(String(255), index=True)


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    room: Mapped[str | None] = mapped_column(String(64), nullable=True)

