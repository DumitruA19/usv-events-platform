from __future__ import annotations

from datetime import datetime, timedelta, timezone

from pathlib import Path

from sqlalchemy.orm import Session

from app.models.enums import EventStatus, ParticipationMode, RegistrationStatus, RoleName
from app.models.event import Event
from app.models.registration import EventRegistration
from app.models.user import User

from .helpers import create_user, login, mock_student_login, seed_roles


def test_mock_google_login_rejects_non_student_domain(client):
    res = client.post("/auth/mock-google-login", json={"email": "x@gmail.com"})
    assert res.status_code == 400


def test_login_accepts_identifier_username(client, db_session: Session):
    seed_roles(db_session)
    create_user(db_session, RoleName.ADMIN.value, "admin", "admin@example.com", "AdminPass!234")
    db_session.commit()
    token = login(client, "admin@example.com", "AdminPass!234")
    assert token


def test_event_approval_workflow(client, db_session: Session):
    seed_roles(db_session)
    create_user(db_session, RoleName.ADMIN.value, "admin", "admin@example.com", "AdminPass!234")
    create_user(db_session, RoleName.ORGANIZER.value, "organizer1", "organizer1@example.com", "OrganizerPass!234")
    db_session.commit()

    org_token = login(client, "organizer1@example.com", "OrganizerPass!234")

    res = client.post(
        "/events",
        headers={"Authorization": f"Bearer {org_token}"},
        json={
            "title": "Test Event",
            "description": "desc",
            "start_dt": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
            "end_dt": (datetime.now(timezone.utc) + timedelta(days=1, hours=1)).isoformat(),
            "participation_mode": "PHYSICAL",
            "requires_registration": True,
            "requires_ticket": False,
            "free_entry": True,
            "has_qr_code": True
        },
    )
    assert res.status_code == 200, res.text
    event_id = res.json()["id"]

    res = client.post(f"/events/{event_id}/submit-for-approval", headers={"Authorization": f"Bearer {org_token}"})
    assert res.status_code == 200, res.text
    assert res.json()["status"] == EventStatus.PENDING_APPROVAL.value

    admin_token = login(client, "admin@example.com", "AdminPass!234")
    res = client.post(f"/events/{event_id}/approve", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    assert res.json()["status"] == EventStatus.PUBLISHED.value


def test_registration_capacity_waiting_list_promotion(client, db_session: Session):
    seed_roles(db_session)
    create_user(db_session, RoleName.ADMIN.value, "admin", "admin@example.com", "AdminPass!234")
    create_user(db_session, RoleName.ORGANIZER.value, "organizer1", "organizer1@example.com", "OrganizerPass!234")
    db_session.commit()

    org_token = login(client, "organizer1@example.com", "OrganizerPass!234")
    now = datetime.now(timezone.utc)
    res = client.post(
        "/events",
        headers={"Authorization": f"Bearer {org_token}"},
        json={
            "title": "Cap 1 Event",
            "description": "",
            "start_dt": (now + timedelta(days=2)).isoformat(),
            "end_dt": (now + timedelta(days=2, hours=1)).isoformat(),
            "participation_mode": "PHYSICAL",
            "requires_registration": True,
            "requires_ticket": True,
            "free_entry": True,
            "capacity": 1,
            "registration_deadline": (now + timedelta(days=1)).isoformat()
        },
    )
    assert res.status_code == 200, res.text
    event_id = res.json()["id"]

    # Publish directly as admin (approval requires pending, so we set status manually in DB for this test)
    ev = db_session.get(Event, event_id)
    ev.status = EventStatus.PUBLISHED.value
    db_session.commit()

    s1_token = mock_student_login(client, "student1@student.usv.ro")
    s2_token = mock_student_login(client, "student2@student.usv.ro")

    res = client.post(f"/events/{event_id}/register", headers={"Authorization": f"Bearer {s1_token}"})
    assert res.status_code == 200, res.text
    assert res.json()["status"] == RegistrationStatus.REGISTERED.value
    assert res.json()["ticket_qr_payload"]

    res = client.post(f"/events/{event_id}/register", headers={"Authorization": f"Bearer {s2_token}"})
    assert res.status_code == 200, res.text
    assert res.json()["status"] == RegistrationStatus.WAITING_LIST.value

    res = client.delete(f"/events/{event_id}/register", headers={"Authorization": f"Bearer {s1_token}"})
    assert res.status_code == 200, res.text

    # student2 should be promoted
    s2 = db_session.query(User).filter(User.email == "student2@student.usv.ro").one()
    reg2 = db_session.query(EventRegistration).filter(EventRegistration.event_id == event_id, EventRegistration.student_id == s2.id).one()
    assert reg2.status == RegistrationStatus.REGISTERED.value
    assert reg2.ticket is not None


def test_feedback_rule_only_after_end(client, db_session: Session):
    seed_roles(db_session)
    create_user(db_session, RoleName.ADMIN.value, "admin", "admin@example.com", "AdminPass!234")
    create_user(db_session, RoleName.ORGANIZER.value, "organizer1", "organizer1@example.com", "OrganizerPass!234")
    db_session.commit()

    org_token = login(client, "organizer1@example.com", "OrganizerPass!234")
    now = datetime.now(timezone.utc)
    res = client.post(
        "/events",
        headers={"Authorization": f"Bearer {org_token}"},
        json={
            "title": "Past Event",
            "description": "",
            "start_dt": (now - timedelta(days=2)).isoformat(),
            "end_dt": (now - timedelta(days=2, hours=-1)).isoformat(),
            "participation_mode": "PHYSICAL",
            "requires_registration": False,
            "requires_ticket": False,
            "free_entry": True
        },
    )
    event_id = res.json()["id"]
    ev = db_session.get(Event, event_id)
    ev.status = EventStatus.PUBLISHED.value
    db_session.commit()

    s1_token = mock_student_login(client, "student1@student.usv.ro")
    res = client.post(
        f"/events/{event_id}/feedback",
        headers={"Authorization": f"Bearer {s1_token}"},
        json={"rating": 5, "comment": "great"},
    )
    assert res.status_code == 200, res.text

    # For a future event, feedback must fail.
    res2 = client.post(
        "/events",
        headers={"Authorization": f"Bearer {org_token}"},
        json={
            "title": "Future Event",
            "description": "",
            "start_dt": (now + timedelta(days=1)).isoformat(),
            "end_dt": (now + timedelta(days=1, hours=1)).isoformat(),
            "participation_mode": "PHYSICAL",
            "requires_registration": False,
            "requires_ticket": False,
            "free_entry": True
        },
    )
    event2_id = res2.json()["id"]
    ev2 = db_session.get(Event, event2_id)
    ev2.status = EventStatus.PUBLISHED.value
    db_session.commit()
    res = client.post(
        f"/events/{event2_id}/feedback",
        headers={"Authorization": f"Bearer {s1_token}"},
        json={"rating": 4, "comment": "nice"},
    )
    assert res.status_code == 400


def test_admin_report_pdf_generates_file(client, db_session: Session, temp_storage_dir):
    seed_roles(db_session)
    create_user(db_session, RoleName.ADMIN.value, "admin", "admin@example.com", "AdminPass!234")
    db_session.commit()

    admin_token = login(client, "admin@example.com", "AdminPass!234")
    res = client.get("/admin/reports/export-pdf", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200, res.text
    path = res.json()["file_path"]
    assert path
    assert Path(path).exists()
