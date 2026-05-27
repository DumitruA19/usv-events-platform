"""admin moderation fields

Revision ID: 0004_admin_moderation_fields
Revises: 0003_scrape_sources
Create Date: 2026-04-28
"""

from alembic import op
import sqlalchemy as sa


revision = "0004_admin_moderation_fields"
down_revision = "0003_scrape_sources"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Users: track updated_at (optional, useful for admin management / auditing).
    op.add_column("users", sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True))

    # Events: store moderation metadata + reasons (reject/cancel).
    op.add_column("events", sa.Column("moderated_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("events", sa.Column("moderated_by_admin_id", sa.Integer(), nullable=True))
    op.add_column("events", sa.Column("rejection_reason", sa.Text(), nullable=True))
    op.add_column("events", sa.Column("cancel_reason", sa.Text(), nullable=True))
    op.create_foreign_key("fk_events_moderated_by_admin", "events", "users", ["moderated_by_admin_id"], ["id"])
    op.create_index(op.f("ix_events_moderated_by_admin_id"), "events", ["moderated_by_admin_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_events_moderated_by_admin_id"), table_name="events")
    op.drop_constraint("fk_events_moderated_by_admin", "events", type_="foreignkey")
    op.drop_column("events", "cancel_reason")
    op.drop_column("events", "rejection_reason")
    op.drop_column("events", "moderated_by_admin_id")
    op.drop_column("events", "moderated_at")
    op.drop_column("users", "updated_at")

