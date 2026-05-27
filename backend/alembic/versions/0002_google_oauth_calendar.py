"""google oauth + calendar links

Revision ID: 0002_google_oauth_calendar
Revises: 0001_init
Create Date: 2026-04-24
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_google_oauth_calendar"
down_revision = "0001_init"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "oauth_accounts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("provider_user_id", sa.String(length=128), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("scopes", sa.Text(), nullable=True),
        sa.Column("refresh_token", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.UniqueConstraint("provider", "provider_user_id", name="uq_oauth_provider_user"),
        sa.UniqueConstraint("provider", "user_id", name="uq_oauth_provider_local_user"),
    )
    op.create_index(op.f("ix_oauth_accounts_user_id"), "oauth_accounts", ["user_id"], unique=False)
    op.create_index(op.f("ix_oauth_accounts_provider"), "oauth_accounts", ["provider"], unique=False)
    op.create_index(op.f("ix_oauth_accounts_provider_user_id"), "oauth_accounts", ["provider_user_id"], unique=False)

    op.create_table(
        "calendar_event_links",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("registration_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("calendar_id", sa.String(length=128), nullable=False, server_default="primary"),
        sa.Column("provider_event_id", sa.String(length=256), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["registration_id"], ["event_registrations.id"]),
        sa.UniqueConstraint("registration_id", name="uq_calendar_link_registration"),
    )
    op.create_index(op.f("ix_calendar_event_links_registration_id"), "calendar_event_links", ["registration_id"], unique=False)
    op.create_index(op.f("ix_calendar_event_links_provider"), "calendar_event_links", ["provider"], unique=False)
    op.create_index(op.f("ix_calendar_event_links_provider_event_id"), "calendar_event_links", ["provider_event_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_calendar_event_links_provider_event_id"), table_name="calendar_event_links")
    op.drop_index(op.f("ix_calendar_event_links_provider"), table_name="calendar_event_links")
    op.drop_index(op.f("ix_calendar_event_links_registration_id"), table_name="calendar_event_links")
    op.drop_table("calendar_event_links")

    op.drop_index(op.f("ix_oauth_accounts_provider_user_id"), table_name="oauth_accounts")
    op.drop_index(op.f("ix_oauth_accounts_provider"), table_name="oauth_accounts")
    op.drop_index(op.f("ix_oauth_accounts_user_id"), table_name="oauth_accounts")
    op.drop_table("oauth_accounts")

