from __future__ import annotations

from pydantic import BaseModel, Field, HttpUrl


class ChatMessageIn(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str = Field(min_length=1, max_length=2000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    page: str | None = Field(default=None, max_length=128)
    history: list[ChatMessageIn] = Field(default_factory=list, max_length=6)
    session_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    used_groq: bool = False
    session_id: str | None = None


class ScrapeSourceCreate(BaseModel):
    url: HttpUrl


class ScrapeRunRequest(BaseModel):
    # Optional override: scrape a single URL once (still admin-only).
    url: HttpUrl | None = None


class ScrapeRunResponse(BaseModel):
    created: int
    duplicates: int
    errors: int
