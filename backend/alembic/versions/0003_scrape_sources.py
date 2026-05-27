"""scrape sources table

Revision ID: 0003_scrape_sources
Revises: 0002_google_oauth_calendar
Create Date: 2026-04-28
"""

from alembic import op
import sqlalchemy as sa


revision = "0003_scrape_sources"
down_revision = "0002_google_oauth_calendar"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "scrape_sources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("url", sa.String(length=1024), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("fail_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("url"),
    )
    op.create_index(op.f("ix_scrape_sources_url"), "scrape_sources", ["url"], unique=False)
    op.create_index(op.f("ix_scrape_sources_is_active"), "scrape_sources", ["is_active"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_scrape_sources_is_active"), table_name="scrape_sources")
    op.drop_index(op.f("ix_scrape_sources_url"), table_name="scrape_sources")
    op.drop_table("scrape_sources")

