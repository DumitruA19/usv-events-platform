from __future__ import annotations

import json
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.integrations.registry import get_integrations
from app.models.enums import EventStatus, ParticipationMode, RoleName, ScrapedDraftStatus
from app.models.event import Event
from app.models.scraping import ScrapedEventDraft
from app.repositories.event_repo import EventRepository
from app.utils.errors import forbidden, not_found


class ScrapingService:
    def __init__(self, db: Session):
        self.db = db
        self.scraper = get_integrations()["scraper"]
        self.events = EventRepository(db)

    def _ensure_admin(self, user) -> None:
        if user.role.name != RoleName.ADMIN.value:
            raise forbidden("Admin only")

    def mock_run(self, admin_user) -> list[ScrapedEventDraft]:
        self._ensure_admin(admin_user)
        raw = self.scraper.run_mock()
        out: list[ScrapedEventDraft] = []
        for item in raw:
            draft = ScrapedEventDraft(
                source=item.get("source", "mock"),
                status=ScrapedDraftStatus.PENDING.value,
                raw_payload_json=json.dumps(item),
                title=item.get("title", "Untitled"),
                description=item.get("description", ""),
                start_dt=datetime.fromisoformat(item["start_dt"]),
                end_dt=datetime.fromisoformat(item["end_dt"]),
                location_text=item.get("location"),
                category_text=item.get("category"),
            )
            self.db.add(draft)
            self.db.flush()
            out.append(draft)
        return out

    def list_drafts(self, admin_user) -> list[ScrapedEventDraft]:
        self._ensure_admin(admin_user)
        stmt = select(ScrapedEventDraft).order_by(ScrapedEventDraft.created_at.desc())
        return list(self.db.scalars(stmt))

    def approve_draft(self, admin_user, draft_id: int) -> Event:
        self._ensure_admin(admin_user)
        d = self.db.get(ScrapedEventDraft, draft_id)
        if not d:
            raise not_found("Draft not found")
        if d.status != ScrapedDraftStatus.PENDING.value:
            raise forbidden("Draft not pending")

        # Create event as published under a system organizer (first organizer in DB).
        from app.models.role import Role
        from app.models.user import User

        organizer = self.db.scalar(
            select(User)
            .join(Role, User.role_id == Role.id)
            .where(Role.name == RoleName.ORGANIZER.value, User.is_active.is_(True))
            .order_by(User.id.asc())
        )
        if not organizer:
            raise forbidden("No organizer available for publishing")

        payload = {}
        try:
            payload = json.loads(d.raw_payload_json or "{}")
        except Exception:
            payload = {}
        raw_mode = str(payload.get("participationMode") or "").upper()
        if raw_mode not in {ParticipationMode.PHYSICAL.value, ParticipationMode.ONLINE.value, ParticipationMode.HYBRID.value}:
            raw_mode = ParticipationMode.PHYSICAL.value

        e = Event(
            title=d.title,
            description=d.description,
            start_dt=d.start_dt,
            end_dt=d.end_dt,
            organizer_id=organizer.id,
            status=EventStatus.PUBLISHED.value,
            participation_mode=raw_mode,
            registration_link=d.source_url,
            free_entry=True,
            requires_registration=False,
            requires_ticket=False,
            has_qr_code=False,
        )
        self.db.add(e)
        self.db.flush()
        d.status = ScrapedDraftStatus.APPROVED.value
        d.rejection_reason = None
        d.approved_by_admin_id = admin_user.id
        d.approved_event_id = e.id
        self.db.flush()
        return e

    def delete_draft(self, admin_user, draft_id: int) -> None:
        self._ensure_admin(admin_user)
        d = self.db.get(ScrapedEventDraft, draft_id)
        if not d:
            raise not_found("Draft not found")
        self.db.delete(d)
