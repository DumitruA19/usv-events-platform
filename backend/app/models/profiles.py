from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    faculty_department_id: Mapped[int | None] = mapped_column(ForeignKey("faculty_departments.id"), nullable=True)
    interests_csv: Mapped[str | None] = mapped_column(String(512), nullable=True)

    user = relationship("User", back_populates="student_profile")
    faculty_department = relationship("FacultyDepartment")


class OrganizerProfile(Base):
    __tablename__ = "organizer_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    faculty_department_id: Mapped[int | None] = mapped_column(ForeignKey("faculty_departments.id"), nullable=True)

    user = relationship("User", back_populates="organizer_profile")
    faculty_department = relationship("FacultyDepartment")

