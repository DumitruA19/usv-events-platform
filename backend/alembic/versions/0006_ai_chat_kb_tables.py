"""ai chat + kb ingestion tables

Revision ID: 0006_ai_chat_kb_tables
Revises: 0005_ai_scrape_draft_fields
Create Date: 2026-05-27
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision = "0006_ai_chat_kb_tables"
down_revision = "0005_ai_scrape_draft_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Postgres-only JSONB; for SQLite tests use JSON (fallback).
    bind = op.get_bind()
    is_sqlite = bind.dialect.name == "sqlite"
    json_type = sa.JSON() if is_sqlite else postgresql.JSONB(astext_type=sa.Text())

    op.create_table(
        "chat_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()") if not is_sqlite else None),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()") if not is_sqlite else None),
    )
    op.create_index(op.f("ix_chat_sessions_user_id"), "chat_sessions", ["user_id"], unique=False)
    op.create_index(op.f("ix_chat_sessions_status"), "chat_sessions", ["status"], unique=False)

    op.create_table(
        "chat_messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("session_id", sa.Integer(), sa.ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()") if not is_sqlite else None),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()") if not is_sqlite else None),
    )
    op.create_index(op.f("ix_chat_messages_session_id"), "chat_messages", ["session_id"], unique=False)
    op.create_index(op.f("ix_chat_messages_user_id"), "chat_messages", ["user_id"], unique=False)
    op.create_index(op.f("ix_chat_messages_role"), "chat_messages", ["role"], unique=False)

    op.create_table(
        "ai_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("session_id", sa.Integer(), sa.ForeignKey("chat_sessions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("provider", sa.String(length=64), nullable=True),
        sa.Column("model", sa.String(length=128), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="skipped"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()") if not is_sqlite else None),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()") if not is_sqlite else None),
    )
    op.create_index(op.f("ix_ai_requests_user_id"), "ai_requests", ["user_id"], unique=False)
    op.create_index(op.f("ix_ai_requests_session_id"), "ai_requests", ["session_id"], unique=False)
    op.create_index(op.f("ix_ai_requests_status"), "ai_requests", ["status"], unique=False)

    op.create_table(
        "scraped_sources_kb",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("base_url", sa.String(length=1024), nullable=True),
        sa.Column("kind", sa.String(length=16), nullable=False, server_default="http"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()") if not is_sqlite else None),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()") if not is_sqlite else None),
    )
    op.create_index(op.f("ix_scraped_sources_kb_is_active"), "scraped_sources_kb", ["is_active"], unique=False)
    op.create_index(op.f("ix_scraped_sources_kb_owner_user_id"), "scraped_sources_kb", ["owner_user_id"], unique=False)

    op.create_table(
        "scraped_pages_kb",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("scraped_sources_kb.id", ondelete="CASCADE"), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=True),
        sa.Column("content_text", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=True),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()") if not is_sqlite else None),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()") if not is_sqlite else None),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()") if not is_sqlite else None),
        sa.UniqueConstraint("source_id", "url", name="uq_scraped_pages_kb_source_url"),
    )
    op.create_index(op.f("ix_scraped_pages_kb_source_id"), "scraped_pages_kb", ["source_id"], unique=False)
    op.create_index(op.f("ix_scraped_pages_kb_content_hash"), "scraped_pages_kb", ["content_hash"], unique=False)

    op.create_table(
        "kb_chunks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("page_id", sa.Integer(), sa.ForeignKey("scraped_pages_kb.id", ondelete="CASCADE"), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=True),
        sa.Column("embedding_model", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()") if not is_sqlite else None),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()") if not is_sqlite else None),
    )
    op.create_index(op.f("ix_kb_chunks_page_id"), "kb_chunks", ["page_id"], unique=False)
    op.create_unique_constraint("uq_kb_chunks_page_chunk", "kb_chunks", ["page_id", "chunk_index"])

    op.create_table(
        "ingestion_jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("scraped_sources_kb.id", ondelete="SET NULL"), nullable=True),
        sa.Column("requested_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="queued"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("stats", json_type, nullable=False, server_default=sa.text("'{}'") if not is_sqlite else None),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()") if not is_sqlite else None),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()") if not is_sqlite else None),
    )
    op.create_index(op.f("ix_ingestion_jobs_status"), "ingestion_jobs", ["status"], unique=False)
    op.create_index(op.f("ix_ingestion_jobs_created_at"), "ingestion_jobs", ["created_at"], unique=False)

    op.create_table(
        "ingestion_job_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("job_id", sa.Integer(), sa.ForeignKey("ingestion_jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("level", sa.String(length=8), nullable=False, server_default="info"),
        sa.Column("message", sa.String(length=255), nullable=False),
        sa.Column("context", json_type, nullable=False, server_default=sa.text("'{}'") if not is_sqlite else None),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()") if not is_sqlite else None),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()") if not is_sqlite else None),
    )
    op.create_index(op.f("ix_ingestion_job_logs_job_id"), "ingestion_job_logs", ["job_id"], unique=False)

    op.create_table(
        "chat_message_kb_refs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("message_id", sa.Integer(), sa.ForeignKey("chat_messages.id", ondelete="CASCADE"), nullable=False),
        sa.Column("chunk_id", sa.Integer(), sa.ForeignKey("kb_chunks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()") if not is_sqlite else None),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()") if not is_sqlite else None),
    )
    op.create_unique_constraint("uq_chat_message_kb_refs", "chat_message_kb_refs", ["message_id", "chunk_id"])
    op.create_index(op.f("ix_chat_message_kb_refs_message_id"), "chat_message_kb_refs", ["message_id"], unique=False)
    op.create_index(op.f("ix_chat_message_kb_refs_chunk_id"), "chat_message_kb_refs", ["chunk_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_chat_message_kb_refs_chunk_id"), table_name="chat_message_kb_refs")
    op.drop_index(op.f("ix_chat_message_kb_refs_message_id"), table_name="chat_message_kb_refs")
    op.drop_constraint("uq_chat_message_kb_refs", "chat_message_kb_refs", type_="unique")
    op.drop_table("chat_message_kb_refs")

    op.drop_index(op.f("ix_ingestion_job_logs_job_id"), table_name="ingestion_job_logs")
    op.drop_table("ingestion_job_logs")

    op.drop_index(op.f("ix_ingestion_jobs_created_at"), table_name="ingestion_jobs")
    op.drop_index(op.f("ix_ingestion_jobs_status"), table_name="ingestion_jobs")
    op.drop_table("ingestion_jobs")

    op.drop_constraint("uq_kb_chunks_page_chunk", "kb_chunks", type_="unique")
    op.drop_index(op.f("ix_kb_chunks_page_id"), table_name="kb_chunks")
    op.drop_table("kb_chunks")

    op.drop_constraint("uq_scraped_pages_kb_source_url", "scraped_pages_kb", type_="unique")
    op.drop_index(op.f("ix_scraped_pages_kb_content_hash"), table_name="scraped_pages_kb")
    op.drop_index(op.f("ix_scraped_pages_kb_source_id"), table_name="scraped_pages_kb")
    op.drop_table("scraped_pages_kb")

    op.drop_index(op.f("ix_scraped_sources_kb_owner_user_id"), table_name="scraped_sources_kb")
    op.drop_index(op.f("ix_scraped_sources_kb_is_active"), table_name="scraped_sources_kb")
    op.drop_table("scraped_sources_kb")

    op.drop_index(op.f("ix_ai_requests_status"), table_name="ai_requests")
    op.drop_index(op.f("ix_ai_requests_session_id"), table_name="ai_requests")
    op.drop_index(op.f("ix_ai_requests_user_id"), table_name="ai_requests")
    op.drop_table("ai_requests")

    op.drop_index(op.f("ix_chat_messages_role"), table_name="chat_messages")
    op.drop_index(op.f("ix_chat_messages_user_id"), table_name="chat_messages")
    op.drop_index(op.f("ix_chat_messages_session_id"), table_name="chat_messages")
    op.drop_table("chat_messages")

    op.drop_index(op.f("ix_chat_sessions_status"), table_name="chat_sessions")
    op.drop_index(op.f("ix_chat_sessions_user_id"), table_name="chat_sessions")
    op.drop_table("chat_sessions")
