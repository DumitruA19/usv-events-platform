from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.password import hash_password
from app.core.config import settings
from app.integrations.registry import get_integrations
from app.models.enums import EventStatus, RoleName
from app.models.event import Event
from app.models.profiles import OrganizerProfile
from app.models.role import Role
from app.models.system import Report
from app.models.user import User
from app.repositories.event_repo import EventRepository
from app.repositories.user_repo import UserRepository
from app.utils.errors import bad_request, forbidden, not_found


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AdminService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)
        self.events = EventRepository(db)
        self.pdf = get_integrations()["pdf"]

    def _ensure_admin(self, user) -> None:
        if user.role.name != RoleName.ADMIN.value:
            raise forbidden("Admin only")

    def list_users(self, admin_user) -> list[User]:
        self._ensure_admin(admin_user)
        return self.users.list_users()

    def update_user(self, admin_user, user_id: int, *, role: str | None, is_active: bool | None) -> User:
        self._ensure_admin(admin_user)
        if admin_user.id == user_id and is_active is False:
            raise bad_request("You cannot deactivate your own account")
        u = self.users.get_by_id(user_id)
        if not u:
            raise not_found("User not found")
        if is_active is not None:
            u.is_active = bool(is_active)
        if role is not None:
            role_norm = role.strip().upper()
            if role_norm not in [RoleName.STUDENT.value, RoleName.ORGANIZER.value, RoleName.ADMIN.value]:
                raise bad_request("Invalid role")
            r = self.db.scalar(select(Role).where(Role.name == role_norm))
            if not r:
                raise bad_request("Roles not seeded")
            u.role_id = r.id
        u.updated_at = utcnow()
        self.db.flush()
        return u

    def create_organizer(self, admin_user, username: str, password: str, display_name: str | None, faculty_department_id: int | None) -> User:
        self._ensure_admin(admin_user)
        if self.users.get_by_username(username):
            raise bad_request("Username already exists")
        role = self.db.scalar(select(Role).where(Role.name == RoleName.ORGANIZER.value))
        if not role:
            raise bad_request("Roles not seeded")
        u = User(username=username, email=None, hashed_password=hash_password(password), role_id=role.id, is_active=True)
        self.users.add(u)
        self.db.add(OrganizerProfile(user_id=u.id, display_name=display_name, faculty_department_id=faculty_department_id))
        self.db.flush()
        return u

    def update_organizer(self, admin_user, user_id: int, **kwargs) -> User:
        self._ensure_admin(admin_user)
        u = self.users.get_by_id(user_id)
        if not u:
            raise not_found("User not found")
        if u.role.name != RoleName.ORGANIZER.value:
            raise bad_request("Not an organizer")
        if kwargs.get("password"):
            u.hashed_password = hash_password(kwargs["password"])
        if kwargs.get("is_active") is not None:
            u.is_active = bool(kwargs["is_active"])
        profile = self.db.scalar(select(OrganizerProfile).where(OrganizerProfile.user_id == u.id))
        if profile:
            if "display_name" in kwargs:
                profile.display_name = kwargs["display_name"]
            if "faculty_department_id" in kwargs:
                profile.faculty_department_id = kwargs["faculty_department_id"]
        self.db.flush()
        return u

    def deactivate_organizer(self, admin_user, user_id: int) -> None:
        self._ensure_admin(admin_user)
        u = self.users.get_by_id(user_id)
        if not u:
            raise not_found("User not found")
        if u.role.name != RoleName.ORGANIZER.value:
            raise bad_request("Not an organizer")
        u.is_active = False
        self.db.flush()

    def pending_events(self, admin_user) -> list[Event]:
        self._ensure_admin(admin_user)
        return self.events.list(statuses=[EventStatus.PENDING_APPROVAL], q=None, date_from=None, date_to=None, category_id=None, organizer_id=None, location_id=None, faculty_department_id=None, participation_mode=None, free_entry=None, requires_registration=None, has_qr_code=None, filter_operator="AND", sort_by="date", sort_dir="asc")

    def list_events(self, admin_user, **kwargs) -> list[Event]:
        self._ensure_admin(admin_user)
        return self.events.list(statuses=None, **kwargs)

    def reject_event(self, admin_user, event_id: int, *, reason: str) -> Event:
        self._ensure_admin(admin_user)
        e = self.db.get(Event, event_id)
        if not e:
            raise not_found("Event not found")
        if e.status != EventStatus.PENDING_APPROVAL.value:
            raise bad_request("Event is not pending approval")
        e.status = EventStatus.REJECTED.value
        e.rejection_reason = reason
        e.moderated_at = utcnow()
        e.moderated_by_admin_id = admin_user.id
        e.updated_at = utcnow()
        self.db.flush()
        return e

    def cancel_event(self, admin_user, event_id: int, *, reason: str) -> Event:
        self._ensure_admin(admin_user)
        e = self.db.get(Event, event_id)
        if not e:
            raise not_found("Event not found")
        e.status = EventStatus.CANCELLED.value
        e.cancel_reason = reason
        e.moderated_at = utcnow()
        e.moderated_by_admin_id = admin_user.id
        e.updated_at = utcnow()
        self.db.flush()
        return e

    def report_events_per_month(self, admin_user) -> list[dict]:
        self._ensure_admin(admin_user)
        dialect = (self.db.get_bind().dialect.name if self.db.get_bind() is not None else "").lower()
        if dialect == "sqlite":
            month_expr = func.strftime("%Y-%m", Event.start_dt)
        else:
            # Postgres: date_trunc + to_char
            month_expr = func.to_char(func.date_trunc("month", Event.start_dt), "YYYY-MM")

        stmt = select(month_expr.label("month"), func.count()).group_by("month").order_by("month")
        rows = self.db.execute(stmt).all()
        return [{"month": r[0], "events": int(r[1])} for r in rows]

    def report_by_organizer(self, admin_user) -> list[dict]:
        self._ensure_admin(admin_user)
        stmt = select(Event.organizer_id, func.count()).group_by(Event.organizer_id)
        rows = self.db.execute(stmt).all()
        return [{"organizer_id": int(r[0]), "events": int(r[1])} for r in rows]

    def report_participation(self, admin_user) -> list[dict]:
        self._ensure_admin(admin_user)
        # Average registrations per event (registered/check-in).
        from app.models.registration import EventRegistration

        stmt = (
            select(EventRegistration.event_id, func.count())
            .where(EventRegistration.status.in_(["REGISTERED", "CHECKED_IN"]))
            .group_by(EventRegistration.event_id)
        )
        rows = self.db.execute(stmt).all()
        return [{"event_id": int(r[0]), "participants": int(r[1])} for r in rows]

    def export_reports_pdf(self, admin_user) -> dict:
        self._ensure_admin(admin_user)
        lines = []
        lines.append("Events per month:")
        for r in self.report_events_per_month(admin_user):
            lines.append(f"- {r['month']}: {r['events']}")
        lines.append("")
        lines.append("Events by organizer:")
        for r in self.report_by_organizer(admin_user):
            lines.append(f"- organizer {r['organizer_id']}: {r['events']}")
        lines.append("")
        lines.append("Participation:")
        for r in self.report_participation(admin_user):
            lines.append(f"- event {r['event_id']}: {r['participants']}")

        out_path = str(Path(settings.storage_dir) / "reports" / f"report-{int(utcnow().timestamp())}.pdf")
        file_path = self.pdf.generate("USV Events Report", lines, out_path)
        rep = Report(type="ADMIN_EXPORT", file_path=file_path)
        self.db.add(rep)
        self.db.flush()
        return {"file_path": file_path}

