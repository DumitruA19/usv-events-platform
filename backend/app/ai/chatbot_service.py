from __future__ import annotations

from sqlalchemy.orm import Session

from app.ai.ai_client import AIClient, AIResult
from app.ai.retrieval_service import RetrievalService
import uuid

from app.models.ai_kb import AIRequest, ChatMessage, ChatMessageKBRef, ChatSession


class ChatbotService:
    def __init__(self, db: Session):
        self.db = db
        self.retrieval = RetrievalService(db)
        self.ai = AIClient()

    def ask(self, *, user_id: str, session_id: str | None, message: str) -> dict:
        """
        RAG skeleton:
        - store user message
        - retrieve chunks with basic text search
        - build prompt
        - generate (safe placeholder unless externally enabled)
        - store assistant message + AI request metadata
        """
        uid = int(user_id)
        # Supabase schema uses UUID ids for sessions/messages; accept UUID strings from frontend.
        sid: uuid.UUID | None = None
        if session_id:
            try:
                sid = uuid.UUID(str(session_id))
            except Exception:
                sid = None
        sid = sid or self._create_session(user_id=uid, title="New chat")
        user_msg_id = self._insert_message(user_id=uid, session_id=sid, role="user", content=message)

        chunks = self.retrieval.search_chunks(message, limit=6)
        if not chunks:
            ai_res = self.ai.generate(
                self._build_prompt(
                    message=message,
                    chunks=["Nu am găsit informații indexate relevante pentru această întrebare."],
                )
            )
        else:
            prompt = self._build_prompt(message=message, chunks=[c.content for c in chunks])
            ai_res = self.ai.generate(prompt)

        req_id = self._insert_ai_request(
            user_id=uid,
            session_id=sid,
            provider=ai_res.provider,
            model=ai_res.model,
            status=ai_res.status,
            error_message=None if ai_res.status == "ok" else "external_call_disabled_or_unconfigured",
        )

        assistant_msg_id = self._insert_message(user_id=uid, session_id=sid, role="assistant", content=ai_res.content)

        # Optional audit links (message -> KB chunks). Skip if schema/types don't match yet.
        for c in chunks:
            try:
                ref = ChatMessageKBRef(message_id=uuid.UUID(str(assistant_msg_id)), chunk_id=int(c.id), score=c.score)
                self.db.add(ref)
            except Exception:
                continue

        return {
            "session_id": str(sid),
            "user_message_id": user_msg_id,
            "assistant_message_id": assistant_msg_id,
            "ai_request_id": req_id,
            "chunks_used": [{"id": c.id} for c in chunks],
            "reply": ai_res.content,
            "provider": ai_res.provider,
            "status": ai_res.status,
        }

    def _build_prompt(self, *, message: str, chunks: list[str]) -> str:
        ctx = "\n\n".join([f"[chunk {i+1}]\n{c}" for i, c in enumerate(chunks)])
        return (
            "You are a helpful assistant for the USV Events Platform.\n"
            "Answer the user question using the provided knowledge chunks when relevant.\n"
            "If the chunks do not contain enough information, say you are not sure.\n\n"
            f"Knowledge chunks:\n{ctx}\n\n"
            f"User question:\n{message}\n"
        )

    def _create_session(self, *, user_id: int, title: str) -> uuid.UUID:
        s = ChatSession(user_id=user_id, title=title, status="active")
        self.db.add(s)
        self.db.flush()
        return uuid.UUID(str(s.id))

    def _insert_message(self, *, user_id: int, session_id: uuid.UUID, role: str, content: str) -> str:
        m = ChatMessage(user_id=user_id, session_id=session_id, role=role, content=content)
        self.db.add(m)
        self.db.flush()
        return str(m.id)

    def _insert_ai_request(self, *, user_id: int, session_id: uuid.UUID, provider: str, model: str, status: str, error_message: str | None) -> str | None:
        # Supabase schema uses `provider_request_id` + `model_id` (optional). Keep minimal auditing.
        req = AIRequest(
            user_id=user_id,
            session_id=session_id,
            provider_request_id=f"{provider}:{model}"[:255] if (provider or model) else None,
            model_id=None,
            status=status,
            prompt_tokens=None,
            completion_tokens=None,
            total_tokens=None,
            error_message=error_message,
            latency_ms=None,
        )
        # Use a savepoint so a mismatch in auditing table doesn't abort the whole chat transaction.
        try:
            with self.db.begin_nested():
                self.db.add(req)
                self.db.flush()
        except Exception:
            return None
        return str(req.id) if req.id else None

