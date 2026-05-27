"""ai scrape draft extra fields

Revision ID: 0005_ai_scrape_draft_fields
Revises: 0004_admin_moderation_fields
Create Date: 2026-05-12
"""

from alembic import op
import sqlalchemy as sa


revision = "0005_ai_scrape_draft_fields"
down_revision = "0004_admin_moderation_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("scraped_event_drafts", sa.Column("source_url", sa.String(length=1024), nullable=True))
    op.add_column("scraped_event_drafts", sa.Column("image_url", sa.String(length=1024), nullable=True))
    op.add_column("scraped_event_drafts", sa.Column("rejection_reason", sa.Text(), nullable=True))
    op.create_index(op.f("ix_scraped_event_drafts_source_url"), "scraped_event_drafts", ["source_url"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_scraped_event_drafts_source_url"), table_name="scraped_event_drafts")
    op.drop_column("scraped_event_drafts", "rejection_reason")
    op.drop_column("scraped_event_drafts", "image_url")
    op.drop_column("scraped_event_drafts", "source_url")
