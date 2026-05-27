from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.integrations.registry import get_integrations
from app.models.enums import RegistrationStatus, RoleName
from app.models.registration import EventRegistration, Ticket, WaitingListEntry
from app.models.system import Notification
from app.repositories.calendar_link_repo import CalendarEventLinkRepository
from app.repositories.event_repo import EventRepository
from app.repositories.oauth_repo import OAuthAccountRepository
from app.repositories.registration_repo import RegistrationRepository
from app.utils.errors import bad_request, forbidden, not_found
from app.core.config import settings


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class RegistrationService:
    def __init__(self, db: Session):
        self.db = db
        self.events = EventRepository(db)
        self.reg = RegistrationRepository(db)
        self.oauth = OAuthAccountRepository(db)
        self.calendar_links = CalendarEventLinkRepository(db)
        self.qr = get_integrations()["qr"]
        self.email = get_integrations()["email"]
        self.calendar = get_integrations()["google_calendar"]

    def register(self, student_user, event_id: int) -> dict:
        if student_user.role.name != RoleName.STUDENT.value:
            raise forbidden("Students only")
        e = self.events.get(event_id)
        if not e:
            raise not_found("Event not found")
        if e.requires_registration is False:
            raise bad_request("This event does not require registration")
        if e.registration_deadline:
            deadline = e.registration_deadline
            if deadline.tzinfo is None:
                deadline = deadline.replace(tzinfo=timezone.utc)
            if utcnow() > deadline:
                raise bad_request("Registration deadline passed")
        existing = self.reg.get_registration(event_id, student_user.id)
        if existing and existing.status != RegistrationStatus.CANCELLED.value:
            raise bad_request("Already registered or on waiting list")

        registered_count = self.reg.count_registered(event_id)
        capacity = e.capacity or 10**9
        if registered_count >= capacity:
            # Waiting list
            position = self.reg.next_waiting_position(event_id)
            if not existing:
                reg = EventRegistration(
                    event_id=event_id,
                    student_id=student_user.id,
                    status=RegistrationStatus.WAITING_LIST.value,
                    registered_at=utcnow(),
                )
                self.reg.add_registration(reg)
            else:
                existing.status = RegistrationStatus.WAITING_LIST.value
                existing.cancelled_at = None
                reg = existing

            self.reg.add_waiting(
                WaitingListEntry(event_id=event_id, student_id=student_user.id, position=position, created_at=utcnow())
            )
            return {"status": reg.status, "message": f"Added to waiting list (position {position})", "ticket_qr_payload": None}

        # Registered
        if not existing:
            reg = EventRegistration(
                event_id=event_id,
                student_id=student_user.id,
                status=RegistrationStatus.REGISTERED.value,
                registered_at=utcnow(),
            )
            self.reg.add_registration(reg)
        else:
            existing.status = RegistrationStatus.REGISTERED.value
            existing.cancelled_at = None
            reg = existing

        ticket_payload = None
        if e.requires_ticket:
            ticket_payload = self.qr.build_payload("ticket", reg.id, salt=str(student_user.id))
            self.reg.add_ticket(Ticket(registration_id=reg.id, qr_payload=ticket_payload, created_at=utcnow()))

        self._notify(student_user.id, "REGISTRATION_CONFIRMED", {"event_id": event_id, "ticket": ticket_payload})
        if student_user.email:
            self.email.send(student_user.email, f"Registration confirmed: {e.title}", "This is a mock email (no real send).")

        self._maybe_add_calendar_event(student_user.id, reg.id, e.title, e.start_dt, e.end_dt)
        return {"status": reg.status, "message": "Registered", "ticket_qr_payload": ticket_payload}

    def cancel(self, student_user, event_id: int) -> dict:
        if student_user.role.name != RoleName.STUDENT.value:
            raise forbidden("Students only")
        e = self.events.get(event_id)
        if not e:
            raise not_found("Event not found")
        reg = self.reg.get_registration(event_id, student_user.id)
        if not reg or reg.status == RegistrationStatus.CANCELLED.value:
            raise bad_request("Not registered")

        prev_status = reg.status
        reg.status = RegistrationStatus.CANCELLED.value
        reg.cancelled_at = utcnow()
        self._maybe_delete_calendar_event(student_user.id, reg.id)

        # Remove waiting list entry if existed.
        entry = self.db.scalar(
            select(WaitingListEntry).where(WaitingListEntry.event_id == event_id, WaitingListEntry.student_id == student_user.id)
        )
        if entry:
            self.db.delete(entry)

        # Promote from waiting list if a seat opens.
        if prev_status == RegistrationStatus.REGISTERED.value and e.capacity is not None:
            waiting = self.reg.list_waiting(event_id)
            if waiting:
                promote = waiting[0]
                self.db.delete(promote)
                next_reg = self.reg.get_registration(event_id, promote.student_id)
                if next_reg and next_reg.status == RegistrationStatus.WAITING_LIST.value:
                    next_reg.status = RegistrationStatus.REGISTERED.value
                    next_reg.cancelled_at = None
                    ticket_payload = None
                    if e.requires_ticket and not next_reg.ticket:
                        ticket_payload = self.qr.build_payload("ticket", next_reg.id, salt=str(promote.student_id))
                        self.reg.add_ticket(Ticket(registration_id=next_reg.id, qr_payload=ticket_payload, created_at=utcnow()))
                    self._notify(promote.student_id, "WAITING_LIST_PROMOTED", {"event_id": event_id, "ticket": ticket_payload})
                    self._maybe_add_calendar_event(promote.student_id, next_reg.id, e.title, e.start_dt, e.end_dt)

        self._notify(student_user.id, "REGISTRATION_CANCELLED", {"event_id": event_id})
        return {"status": reg.status, "message": "Cancelled"}

    def _maybe_add_calendar_event(self, user_id: int, registration_id: int, title: str, start_dt: datetime, end_dt: datetime) -> None:
        # Only if the user connected Google and we don't already have a link.
        if self.calendar_links.get_by_registration(registration_id):
            return
        acct = self.oauth.get_by_user(user_id, "google")
        if not acct or not acct.refresh_token:
            return

        try:
            ev = self.calendar.create_event(
                acct.refresh_token,
                calendar_id=settings.google_calendar_id,
                title=title,
                start_dt=start_dt,
                end_dt=end_dt,
                timezone=settings.default_timezone,
            )
            provider_event_id = str(ev.get("id") or "")
            if not provider_event_id:
                return
            self.calendar_links.create_link(
                registration_id=registration_id,
                provider="google",
                calendar_id=settings.google_calendar_id,
                provider_event_id=provider_event_id,
            )
        except Exception:
            # Calendar is best-effort: registration must still succeed even if Google call fails.
            return

    def _maybe_delete_calendar_event(self, user_id: int, registration_id: int) -> None:
        link = self.calendar_links.get_by_registration(registration_id)
        if not link:
            return
        acct = self.oauth.get_by_user(user_id, "google")
        try:
            if acct and acct.refresh_token:
                self.calendar.delete_event(acct.refresh_token, calendar_id=link.calendar_id, provider_event_id=link.provider_event_id)
        except Exception:
            pass
        try:
            self.calendar_links.delete_link(link)
        except Exception:
            pass

    def list_participants(self, user, event_id: int) -> list[EventRegistration]:
        e = self.events.get(event_id)
        if not e:
            raise not_found("Event not found")
        if user.role.name == RoleName.ORGANIZER.value and e.organizer_id != user.id:
            raise forbidden("Organizers can view participants only for their own events")
        if user.role.name not in [RoleName.ORGANIZER.value, RoleName.ADMIN.value]:
            raise forbidden("Not allowed")
        return self.reg.list_participants(event_id)

    def list_waiting(self, user, event_id: int) -> list[WaitingListEntry]:
        e = self.events.get(event_id)
        if not e:
            raise not_found("Event not found")
        if user.role.name == RoleName.ORGANIZER.value and e.organizer_id != user.id:
            raise forbidden("Organizers can view waiting list only for their own events")
        if user.role.name not in [RoleName.ORGANIZER.value, RoleName.ADMIN.value]:
            raise forbidden("Not allowed")
        return self.reg.list_waiting(event_id)

    def export_participants_csv(self, user, event_id: int) -> str:
        participants = self.list_participants(user, event_id)
        out = io.StringIO()
        writer = csv.writer(out)
        writer.writerow(["student_id", "email", "status", "registered_at", "ticket_qr_payload"])
        for p in participants:
            writer.writerow([p.student_id, p.student.email if p.student else None, p.status, p.registered_at.isoformat(), p.ticket.qr_payload if p.ticket else None])
        return out.getvalue()

    def check_in(self, user, event_id: int, qr_payload: str) -> dict:
        e = self.events.get(event_id)
        if not e:
            raise not_found("Event not found")
        if user.role.name == RoleName.ORGANIZER.value and e.organizer_id != user.id:
            raise forbidden("Organizers can check-in only their own events")
        if user.role.name not in [RoleName.ORGANIZER.value, RoleName.ADMIN.value]:
            raise forbidden("Not allowed")
        ticket = self.reg.find_ticket(qr_payload)
        if not ticket or not ticket.registration:
            raise bad_request("Invalid ticket")
        if ticket.registration.event_id != event_id:
            raise bad_request("Ticket not for this event")
        if ticket.registration.status not in [RegistrationStatus.REGISTERED.value, RegistrationStatus.CHECKED_IN.value]:
            raise bad_request("Registration not active")
        ticket.registration.status = RegistrationStatus.CHECKED_IN.value
        ticket.registration.checked_in_at = utcnow()
        ticket.checked_in_at = utcnow()
        self.db.flush()
        self._notify(ticket.registration.student_id, "CHECKED_IN", {"event_id": event_id})
        return {"status": ticket.registration.status, "message": "Checked in"}

    def _notify(self, user_id: int, type: str, payload: dict) -> None:
        self.db.add(Notification(user_id=user_id, type=type, payload_json=json.dumps(payload), created_at=utcnow()))
        self.db.flush()
