from __future__ import annotations

from sqlalchemy.orm import Session

from app.ai.ai_client import AIClient
from app.ai.db import exec_one
from app.ai.retrieval_service import RetrievalService


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
        session_id = session_id or self._create_session(user_id=user_id, title="New chat")
        user_msg_id = self._insert_message(user_id=user_id, session_id=session_id, role="user", content=message)

        chunks = self.retrieval.search_chunks(message, limit=6)
        prompt = self._build_prompt(message=message, chunks=[c.content for c in chunks])
        ai_res = self.ai.generate(prompt)

        req_id = self._insert_ai_request(
            user_id=user_id,
            session_id=session_id,
            provider=ai_res.provider,
            model=ai_res.model,
            status=ai_res.status,
            error_message=None if ai_res.status == "ok" else "external_call_disabled_or_unconfigured",
        )

        assistant_msg_id = self._insert_message(user_id=user_id, session_id=session_id, role="assistant", content=ai_res.content)

        for c in chunks:
            exec_one(
                self.db,
                """
                insert into public.chat_message_kb_refs (message_id, chunk_id, score)
                values (:message_id, :chunk_id, :score)
                on conflict (message_id, chunk_id) do nothing
                returning id
                """,
                {"message_id": assistant_msg_id, "chunk_id": c.id, "score": c.score},
            )

        return {
            "session_id": session_id,
            "user_message_id": user_msg_id,
            "assistant_message_id": assistant_msg_id,
            "ai_request_id": req_id,
            "chunks_used": [{"id": c.id} for c in chunks],
            "reply": ai_res.content,
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

    def _create_session(self, *, user_id: str, title: str) -> str:
        row = exec_one(
            self.db,
            """
            insert into public.chat_sessions (user_id, title)
            values (:user_id, :title)
            returning id
            """,
            {"user_id": user_id, "title": title},
        )
        if not row or not row.get("id"):
            raise RuntimeError("Failed to create chat session (missing tables?)")
        return str(row["id"])

    def _insert_message(self, *, user_id: str, session_id: str, role: str, content: str) -> str:
        row = exec_one(
            self.db,
            """
            insert into public.chat_messages (user_id, session_id, role, content)
            values (:user_id, :session_id, :role, :content)
            returning id
            """,
            {"user_id": user_id, "session_id": session_id, "role": role, "content": content},
        )
        if not row or not row.get("id"):
            raise RuntimeError("Failed to insert chat message (missing tables?)")
        return str(row["id"])

    def _insert_ai_request(self, *, user_id: str, session_id: str, provider: str, model: str, status: str, error_message: str | None) -> str | None:
        row = exec_one(
            self.db,
            """
            insert into public.ai_requests (user_id, session_id, status, error_message)
            values (:user_id, :session_id, :status, :error_message)
            returning id
            """,
            {"user_id": user_id, "session_id": session_id, "status": status, "error_message": error_message},
        )
        return str(row["id"]) if row and row.get("id") else None

