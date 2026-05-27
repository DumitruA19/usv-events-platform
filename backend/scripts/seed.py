from __future__ import annotations

import sys
import os

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import select

# Allow running as `python scripts/seed.py` from the backend folder.
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.auth.password import hash_password
from app.core.config import settings
from app.core.database import SessionLocal, init_storage_dirs
from app.integrations.registry import get_integrations
from app.models.catalog import EventCategory, FacultyDepartment, Location
from app.models.enums import EventStatus, ParticipationMode, RegistrationStatus, RoleName, ScrapedDraftStatus
from app.models.event import Event, EventMaterial, EventSponsor, Sponsor
from app.models.feedback import Feedback, FavoriteEvent
from app.models.profiles import OrganizerProfile, StudentProfile
from app.models.registration import EventRegistration, Ticket, WaitingListEntry
from app.models.role import Role
from app.models.scraping import ScrapedEventDraft
from app.models.system import AuditLog, Notification, Reminder, Report
from app.models.user import User


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def get_or_create_role(db, name: RoleName) -> Role:
    r = db.scalar(select(Role).where(Role.name == name.value))
    if r:
        return r
    r = Role(name=name.value)
    db.add(r)
    db.flush()
    return r


def get_or_create_category(db, name: str) -> EventCategory:
    c = db.scalar(select(EventCategory).where(EventCategory.name == name))
    if c:
        return c
    c = EventCategory(name=name)
    db.add(c)
    db.flush()
    return c


def get_or_create_facdep(db, faculty: str, department: str) -> FacultyDepartment:
    fd = db.scalar(select(FacultyDepartment).where(FacultyDepartment.faculty == faculty, FacultyDepartment.department == department))
    if fd:
        return fd
    fd = FacultyDepartment(faculty=faculty, department=department)
    db.add(fd)
    db.flush()
    return fd


def get_or_create_location(db, name: str, address: str | None = None, room: str | None = None) -> Location:
    loc = db.scalar(select(Location).where(Location.name == name))
    if loc:
        return loc
    loc = Location(name=name, address=address, room=room)
    db.add(loc)
    db.flush()
    return loc


def get_or_create_user(db, *, role: Role, username: str | None, email: str | None, password: str | None) -> User:
    if username:
        existing = db.scalar(select(User).where(User.username == username))
        if existing:
            # Repair existing rows (common when switching DBs / running seed multiple times).
            if existing.role_id != role.id:
                existing.role_id = role.id
            if password and not existing.hashed_password:
                existing.hashed_password = hash_password(password)
            if existing.is_active is not True:
                existing.is_active = True
            return existing
    if email:
        existing = db.scalar(select(User).where(User.email == email))
        if existing:
            if existing.role_id != role.id:
                existing.role_id = role.id
            if password and not existing.hashed_password:
                existing.hashed_password = hash_password(password)
            if existing.is_active is not True:
                existing.is_active = True
            return existing
    u = User(
        username=username,
        email=email,
        hashed_password=hash_password(password) if password else None,
        role_id=role.id,
        is_active=True,
        created_at=utcnow(),
    )
    db.add(u)
    db.flush()
    return u


def main() -> None:
    init_storage_dirs()
    qr = get_integrations()["qr"]

    db = SessionLocal()
    try:
        # Roles
        admin_role = get_or_create_role(db, RoleName.ADMIN)
        organizer_role = get_or_create_role(db, RoleName.ORGANIZER)
        student_role = get_or_create_role(db, RoleName.STUDENT)

        # Catalog
        fd_fiesc = get_or_create_facdep(db, "FIESC", "Computer Science")
        fd_economics = get_or_create_facdep(db, "FEFS", "Economics")

        cat_lecture = get_or_create_category(db, "Lecture")
        cat_workshop = get_or_create_category(db, "Workshop")
        cat_career = get_or_create_category(db, "Career")

        loc_aud = get_or_create_location(db, "USV - Auditorium A", "Str. Universitatii 13", "A1")
        loc_lab = get_or_create_location(db, "USV - Lab 42", "Str. Universitatii 13", "L42")
        loc_online = get_or_create_location(db, "Online", None, None)

        # Users (credentials come from env; use safe demo defaults only in local env).
        def env_or_default(name: str, default: str) -> str | None:
            v = os.getenv(name)
            if v is not None and str(v).strip():
                return str(v).strip()
            return default if settings.env.lower() == "local" else None

        admin_username = env_or_default("SEED_ADMIN_USERNAME", "admin")
        admin_password = env_or_default("SEED_ADMIN_PASSWORD", "AdminPass!234")
        org1_username = env_or_default("SEED_ORG1_USERNAME", "organizer1")
        org1_password = env_or_default("SEED_ORG1_PASSWORD", "OrganizerPass!234")
        org2_username = env_or_default("SEED_ORG2_USERNAME", "organizer2")
        org2_password = env_or_default("SEED_ORG2_PASSWORD", "OrganizerPass!234")

        admin = get_or_create_user(db, role=admin_role, username=admin_username, email=None, password=admin_password) if admin_username else None
        org1 = get_or_create_user(db, role=organizer_role, username=org1_username, email=None, password=org1_password) if org1_username else None
        org2 = get_or_create_user(db, role=organizer_role, username=org2_username, email=None, password=org2_password) if org2_username else None

        if admin is None or org1 is None or org2 is None:
            print("Seed note: admin/organizer demo users not fully created (set SEED_* env vars or ENV=local).")

        if org1 and not db.scalar(select(OrganizerProfile).where(OrganizerProfile.user_id == org1.id)):
            db.add(OrganizerProfile(user_id=org1.id, display_name="Organizer One", faculty_department_id=fd_fiesc.id))
        if org2 and not db.scalar(select(OrganizerProfile).where(OrganizerProfile.user_id == org2.id)):
            db.add(OrganizerProfile(user_id=org2.id, display_name="Organizer Two", faculty_department_id=fd_economics.id))

        students = []
        for i in range(1, 6):
            email = f"student{i}@student.usv.ro"
            u = get_or_create_user(db, role=student_role, username=None, email=email, password=None)
            if not db.scalar(select(StudentProfile).where(StudentProfile.user_id == u.id)):
                db.add(StudentProfile(user_id=u.id, full_name=f"Student {i}", faculty_department_id=fd_fiesc.id))
            students.append(u)

        # Sponsors
        sp1 = db.scalar(select(Sponsor).where(Sponsor.name == "TechCorp")) or Sponsor(name="TechCorp", logo_path=None)
        sp2 = db.scalar(select(Sponsor).where(Sponsor.name == "CampusBank")) or Sponsor(name="CampusBank", logo_path=None)
        db.add_all([sp1, sp2])
        db.flush()

        now = utcnow()

        def create_event_if_missing(title: str, **kwargs) -> Event:
            existing = db.scalar(select(Event).where(Event.title == title))
            if existing:
                return existing
            desc = kwargs.pop("description", "")
            ev = Event(title=title, description=desc, created_at=now, updated_at=now, **kwargs)
            db.add(ev)
            db.flush()
            return ev

        past_event = create_event_if_missing(
            "Workshop: Practical Git",
            description="Hands-on Git workflows for teams (seeded).",
            start_dt=now - timedelta(days=3),
            end_dt=now - timedelta(days=3, hours=-2),
            status=EventStatus.PUBLISHED.value,
            participation_mode=ParticipationMode.PHYSICAL.value,
            organizer_id=org1.id,
            category_id=cat_workshop.id,
            faculty_department_id=fd_fiesc.id,
            location_id=loc_lab.id,
            free_entry=True,
            requires_registration=True,
            requires_ticket=True,
            capacity=2,
            registration_deadline=now - timedelta(days=4),
            has_qr_code=True,
        )

        upcoming_event = create_event_if_missing(
            "Public Lecture: AI in Education",
            description="A public lecture about AI in education (seeded).",
            start_dt=now + timedelta(days=5),
            end_dt=now + timedelta(days=5, hours=2),
            status=EventStatus.PUBLISHED.value,
            participation_mode=ParticipationMode.HYBRID.value,
            organizer_id=org1.id,
            category_id=cat_lecture.id,
            faculty_department_id=fd_fiesc.id,
            location_id=loc_aud.id,
            free_entry=True,
            requires_registration=True,
            requires_ticket=False,
            capacity=50,
            registration_deadline=now + timedelta(days=4),
            has_qr_code=True,
        )

        pending_event = create_event_if_missing(
            "Career Fair Spring (Pending)",
            description="Pending approval example.",
            start_dt=now + timedelta(days=12),
            end_dt=now + timedelta(days=12, hours=4),
            status=EventStatus.PENDING_APPROVAL.value,
            participation_mode=ParticipationMode.PHYSICAL.value,
            organizer_id=org2.id,
            category_id=cat_career.id,
            faculty_department_id=fd_economics.id,
            location_id=loc_aud.id,
            free_entry=True,
            requires_registration=False,
            requires_ticket=False,
            capacity=None,
            registration_deadline=None,
            has_qr_code=False,
        )

        draft_event = create_event_if_missing(
            "Organizer Draft Event",
            description="Draft example.",
            start_dt=now + timedelta(days=20),
            end_dt=now + timedelta(days=20, hours=1),
            status=EventStatus.DRAFT.value,
            participation_mode=ParticipationMode.ONLINE.value,
            organizer_id=org1.id,
            category_id=cat_workshop.id,
            faculty_department_id=fd_fiesc.id,
            location_id=loc_online.id,
            free_entry=True,
            requires_registration=True,
            requires_ticket=True,
            capacity=1,
            registration_deadline=now + timedelta(days=19),
            has_qr_code=True,
        )

        # Sponsor links
        if not db.scalar(select(EventSponsor).where(EventSponsor.event_id == upcoming_event.id, EventSponsor.sponsor_id == sp1.id)):
            db.add(EventSponsor(event_id=upcoming_event.id, sponsor_id=sp1.id, tier="Gold"))
        if not db.scalar(select(EventSponsor).where(EventSponsor.event_id == past_event.id, EventSponsor.sponsor_id == sp2.id)):
            db.add(EventSponsor(event_id=past_event.id, sponsor_id=sp2.id, tier="Silver"))

        # Materials metadata + local file
        mat_dir = Path(settings.storage_dir) / "materials" / str(upcoming_event.id)
        mat_dir.mkdir(parents=True, exist_ok=True)
        demo_file = mat_dir / "slides-demo.txt"
        if not demo_file.exists():
            demo_file.write_text("Demo material placeholder (local file).", encoding="utf-8")
        if not db.scalar(select(EventMaterial).where(EventMaterial.event_id == upcoming_event.id, EventMaterial.filename == "slides-demo.txt")):
            db.add(
                EventMaterial(
                    event_id=upcoming_event.id,
                    filename="slides-demo.txt",
                    content_type="text/plain",
                    size_bytes=demo_file.stat().st_size,
                    stored_path=str(demo_file),
                )
            )

        # Registrations + waiting list scenario for past_event (capacity=2)
        for idx, student in enumerate(students[:3]):
            existing = db.scalar(select(EventRegistration).where(EventRegistration.event_id == past_event.id, EventRegistration.student_id == student.id))
            if existing:
                continue
            if idx < 2:
                reg = EventRegistration(event_id=past_event.id, student_id=student.id, status=RegistrationStatus.REGISTERED.value, registered_at=now - timedelta(days=10))
                db.add(reg)
                db.flush()
                ticket_payload = qr.build_payload("ticket", reg.id, salt=str(student.id))
                db.add(Ticket(registration_id=reg.id, qr_payload=ticket_payload, created_at=now - timedelta(days=10)))
            else:
                reg = EventRegistration(event_id=past_event.id, student_id=student.id, status=RegistrationStatus.WAITING_LIST.value, registered_at=now - timedelta(days=10))
                db.add(reg)
                db.flush()
                db.add(WaitingListEntry(event_id=past_event.id, student_id=student.id, position=1, created_at=now - timedelta(days=10)))

        # Registration for upcoming_event
        s1 = students[0]
        if not db.scalar(select(EventRegistration).where(EventRegistration.event_id == upcoming_event.id, EventRegistration.student_id == s1.id)):
            reg = EventRegistration(event_id=upcoming_event.id, student_id=s1.id, status=RegistrationStatus.REGISTERED.value, registered_at=now - timedelta(hours=1))
            db.add(reg)

        # Feedback for past_event (allowed since ended)
        if not db.scalar(select(Feedback).where(Feedback.event_id == past_event.id, Feedback.student_id == students[0].id)):
            db.add(Feedback(event_id=past_event.id, student_id=students[0].id, rating=5, comment="Great workshop, very helpful!", sentiment_label="POSITIVE", created_at=now - timedelta(days=2)))

        # Favorites + reminders (demo)
        if not db.scalar(select(FavoriteEvent).where(FavoriteEvent.event_id == upcoming_event.id, FavoriteEvent.student_id == students[0].id)):
            db.add(FavoriteEvent(event_id=upcoming_event.id, student_id=students[0].id, created_at=now))
        if not db.scalar(select(Reminder).where(Reminder.user_id == students[0].id, Reminder.event_id == upcoming_event.id)):
            db.add(Reminder(user_id=students[0].id, event_id=upcoming_event.id, scheduled_at=now + timedelta(days=4)))

        # Notifications/audit logs (demo trace)
        if admin:
            db.add(Notification(user_id=admin.id, type="SEED", payload_json=json.dumps({"status": "completed"}), created_at=now))
            db.add(AuditLog(actor_id=admin.id, action="SEED_RUN", entity_type=None, entity_id=None, details_json=json.dumps({"when": now.isoformat()})))

        # Reports (demo placeholder)
        report_path = Path(settings.storage_dir) / "reports" / "demo-report.txt"
        if not report_path.exists():
            report_path.write_text("Demo report placeholder.", encoding="utf-8")
        if not db.scalar(select(Report).where(Report.type == "DEMO")):
            db.add(Report(type="DEMO", file_path=str(report_path), generated_at=now))

        # Scraped drafts (demo)
        if not db.scalar(select(ScrapedEventDraft).where(ScrapedEventDraft.source == "mock-local-html")):
            db.add(
                ScrapedEventDraft(
                    source="mock-local-html",
                    status=ScrapedDraftStatus.PENDING.value,
                    raw_payload_json=json.dumps({"source": "mock-local-html", "note": "seeded"}),
                    title="Seeded Scraped Draft",
                    description="This is a seeded scraped draft event.",
                    start_dt=now + timedelta(days=30),
                    end_dt=now + timedelta(days=30, hours=2),
                    location_text="USV Campus",
                    category_text="Lecture",
                    created_at=now,
                    approved_by_admin_id=None,
                    approved_event_id=None,
                )
            )

        db.commit()
        print("Seed completed.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
