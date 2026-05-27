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
    # Use batch mode so migrations work on SQLite (no ALTER CONSTRAINT support)
    # and on Postgres/Supabase.
    with op.batch_alter_table("users") as batch:
        batch.add_column(sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True))

    with op.batch_alter_table("events") as batch:
        batch.add_column(sa.Column("moderated_at", sa.DateTime(timezone=True), nullable=True))
        batch.add_column(sa.Column("moderated_by_admin_id", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("rejection_reason", sa.Text(), nullable=True))
        batch.add_column(sa.Column("cancel_reason", sa.Text(), nullable=True))
        batch.create_foreign_key("fk_events_moderated_by_admin", "users", ["moderated_by_admin_id"], ["id"])
        batch.create_index(op.f("ix_events_moderated_by_admin_id"), ["moderated_by_admin_id"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("events") as batch:
        batch.drop_index(op.f("ix_events_moderated_by_admin_id"))
        batch.drop_constraint("fk_events_moderated_by_admin", type_="foreignkey")
        batch.drop_column("cancel_reason")
        batch.drop_column("rejection_reason")
        batch.drop_column("moderated_by_admin_id")
        batch.drop_column("moderated_at")

    with op.batch_alter_table("users") as batch:
        batch.drop_column("updated_at")
