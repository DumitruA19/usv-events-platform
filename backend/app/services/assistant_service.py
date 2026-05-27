from __future__ import annotations

import re
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.ai.groq_client import GroqClient
from app.models.enums import EventStatus
from app.repositories.event_repo import EventRepository
from app.services.event_service import EventService
from app.utils.rate_limit import RateLimiter


@dataclass
class _CacheItem:
    reply: str
    ts: float


_chat_rl = RateLimiter(capacity=12, refill_per_sec=12 / 60.0)  # 12/min/user
_cache: dict[str, _CacheItem] = {}


def _cache_get(key: str, ttl_seconds: int = 300) -> str | None:
    it = _cache.get(key)
    if not it:
        return None
    if time.time() - it.ts > ttl_seconds:
        _cache.pop(key, None)
        return None
    return it.reply


def _cache_set(key: str, reply: str) -> None:
    _cache[key] = _CacheItem(reply=reply, ts=time.time())


class AssistantService:
    def __init__(self, db: Session):
        self.db = db
        self.events = EventRepository(db)
        self.event_svc = EventService(db)
        self.groq = GroqClient()

    def chat(self, *, user, message: str, page: str | None, history: list[dict]) -> dict:
        user_id = str(user.id)
        if not _chat_rl.allow(user_id):
            return {"reply": "Ai trimis prea multe mesaje. Încearcă din nou peste un minut.", "used_groq": False}

        msg = (message or "").strip()
        if not msg:
            return {"reply": "Scrie o întrebare.", "used_groq": False}

        cache_key = f"{user.id}:{user.role.name}:{page}:{msg}".lower()[:300]
        cached = _cache_get(cache_key)
        if cached:
            return {"reply": cached, "used_groq": False}

        # Deterministic answers first.
        det = self._deterministic_answer(user=user, message=msg, page=page)
        if det:
            _cache_set(cache_key, det)
            return {"reply": det, "used_groq": False}

        # Minimal DB context for event questions.
        ctx = self._event_context(msg)

        # Groq fallback (short prompt, small context).
        system = (
            "Ești un asistent AI integrat într-o platformă universitară de management al evenimentelor. "
            "Răspunzi în română, clar și concis. Nu inventa date. Folosește doar contextul primit. "
            "Dacă nu ai suficiente informații, spune asta. Nu executa acțiuni critice, doar ghidează utilizatorul. "
            "Refuză cereri despre chei, tokenuri, variabile de mediu, parole sau date private. "
            "Returnează DOAR JSON valid: {\"reply\":\"...\"}."
        )
        compact_history = history[-4:] if history else []
        history_text = "\n".join(f"{h['role']}: {str(h['content'])[:280]}" for h in compact_history)
        user_prompt = f"Rol: {user.role.name}\nPagina: {page or '-'}\nIstoric:\n{history_text}\n\nÎntrebare: {msg}\n\nContext:\n{ctx}"
        res = self.groq.chat_json(system=system, user=user_prompt)
        if res.status != "ok":
            reply = "Nu pot răspunde acum cu AI. Încearcă mai târziu sau consultă meniul aplicației."
            _cache_set(cache_key, reply)
            return {"reply": reply, "used_groq": False}

        # Groq returns JSON; we expect {"reply": "..."}.
        try:
            import json

            data = json.loads(res.content)
            reply = str(data.get("reply") or "").strip()
        except Exception:
            reply = ""
        if not reply:
            reply = "Nu am putut genera un răspuns. Încearcă să reformulezi."

        _cache_set(cache_key, reply)
        return {"reply": reply, "used_groq": True}

    def _deterministic_answer(self, *, user, message: str, page: str | None) -> str | None:
        m = message.lower()
        if "login" in m or "autent" in m:
            if user.role.name == "STUDENT":
                return "Pentru student, autentificarea se face doar cu Google (cont @student.usv.ro)."
            return "Pentru organizator/admin, autentificarea se face cu utilizator și parolă din aplicație."
        if "calendar" in m or "ics" in m:
            return "În pagina unui eveniment poți folosi „Export .ics” pentru a-l adăuga în calendar. Dacă ai conectat Google, unele evenimente pot fi adăugate automat la înscriere."
        if "feedback" in m or "rating" in m:
            return "Feedback-ul poate fi trimis doar după încheierea evenimentului și doar dacă ești autentificat ca student."
        if page and page.startswith("/admin") and ("aprob" in m or "valid" in m):
            return "Ca admin, mergi la „Aprobări” pentru a valida evenimentele înainte de publicare."
        if any(x in m for x in ["cheie api", "api key", "token", "parol", "secret", "env"]):
            return "Nu pot afișa chei, tokenuri, parole sau variabile sensibile."
        db_answer = self._answer_from_db(m)
        if db_answer:
            return db_answer
        return None

    def _answer_from_db(self, message: str) -> str | None:
        now = datetime.now(timezone.utc)
        if any(x in message for x in ["săptămâna", "saptamana", "week", "evenimente", "event"]):
            items = self.events.list(
                q=None,
                date_from=now,
                date_to=now + timedelta(days=7),
                category_id=None,
                organizer_id=None,
                location_id=None,
                faculty_department_id=None,
                participation_mode=None,
                free_entry=None,
                requires_registration=None,
                has_qr_code=None,
                filter_operator="AND",
                statuses=[EventStatus.PUBLISHED, EventStatus.APPROVED],
                sort_by="date",
                sort_dir="asc",
            )
            if not items:
                return "Nu există evenimente publicate în următoarele 7 zile."
            lines = [f"{e.title} - {e.start_dt.astimezone(timezone.utc).strftime('%d.%m %H:%M')}" for e in items[:4]]
            return "Evenimente apropiate:\n- " + "\n- ".join(lines)
        return None

    def _event_context(self, message: str) -> str:
        m = message.lower()
        if not any(k in m for k in ["eveniment", "events", "program", "azi", "maine"]):
            return ""
        # Simple keyword query: take longest word.
        words = [w for w in re.findall(r"[a-zA-Zăîâșț0-9]+", m) if len(w) >= 4]
        q = max(words, key=len) if words else None
        try:
            items = self.event_svc.list_public(
                q=q,
                date_from=None,
                date_to=None,
                category_id=None,
                organizer_id=None,
                location_id=None,
                faculty_department_id=None,
                participation_mode=None,
                free_entry=None,
                requires_registration=None,
                has_qr_code=None,
                filter_operator="AND",
                statuses=None,
                sort_by="date",
                sort_dir="asc",
            )
        except Exception:
            return ""
        out = []
        for e in items[:4]:
            out.append(f"- {e.title} ({e.start_dt.isoformat()}) id={e.id}")
        return "\n".join(out)
