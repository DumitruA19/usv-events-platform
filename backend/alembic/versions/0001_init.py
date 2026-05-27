"""initial schema

Revision ID: 0001_init
Revises:
Create Date: 2026-04-24
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=32), nullable=False),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_roles_name"), "roles", ["name"], unique=False)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("username", sa.String(length=64), nullable=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"]),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=False)
    op.create_index(op.f("ix_users_role_id"), "users", ["role_id"], unique=False)

    op.create_table(
        "event_categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_event_categories_name"), "event_categories", ["name"], unique=False)

    op.create_table(
        "faculty_departments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("faculty", sa.String(length=255), nullable=False),
        sa.Column("department", sa.String(length=255), nullable=False),
    )
    op.create_index(op.f("ix_faculty_departments_faculty"), "faculty_departments", ["faculty"], unique=False)
    op.create_index(op.f("ix_faculty_departments_department"), "faculty_departments", ["department"], unique=False)

    op.create_table(
        "locations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("address", sa.String(length=255), nullable=True),
        sa.Column("room", sa.String(length=64), nullable=True),
    )
    op.create_index(op.f("ix_locations_name"), "locations", ["name"], unique=False)

    op.create_table(
        "student_profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("faculty_department_id", sa.Integer(), nullable=True),
        sa.Column("interests_csv", sa.String(length=512), nullable=True),
        sa.ForeignKeyConstraint(["faculty_department_id"], ["faculty_departments.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_student_profiles_user_id"), "student_profiles", ["user_id"], unique=False)

    op.create_table(
        "organizer_profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("faculty_department_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["faculty_department_id"], ["faculty_departments.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_organizer_profiles_user_id"), "organizer_profiles", ["user_id"], unique=False)

    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("start_dt", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_dt", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("participation_mode", sa.String(length=16), nullable=False),
        sa.Column("organizer_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("faculty_department_id", sa.Integer(), nullable=True),
        sa.Column("location_id", sa.Integer(), nullable=True),
        sa.Column("registration_link", sa.String(length=512), nullable=True),
        sa.Column("free_entry", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("requires_registration", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("requires_ticket", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("has_qr_code", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("capacity", sa.Integer(), nullable=True),
        sa.Column("registration_deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column("max_material_files", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("max_material_mb", sa.Integer(), nullable=False, server_default="20"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["event_categories.id"]),
        sa.ForeignKeyConstraint(["faculty_department_id"], ["faculty_departments.id"]),
        sa.ForeignKeyConstraint(["location_id"], ["locations.id"]),
        sa.ForeignKeyConstraint(["organizer_id"], ["users.id"]),
    )
    op.create_index(op.f("ix_events_title"), "events", ["title"], unique=False)
    op.create_index(op.f("ix_events_start_dt"), "events", ["start_dt"], unique=False)
    op.create_index(op.f("ix_events_end_dt"), "events", ["end_dt"], unique=False)
    op.create_index(op.f("ix_events_status"), "events", ["status"], unique=False)
    op.create_index(op.f("ix_events_organizer_id"), "events", ["organizer_id"], unique=False)

    op.create_table(
        "sponsors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("logo_path", sa.String(length=512), nullable=True),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_sponsors_name"), "sponsors", ["name"], unique=False)

    op.create_table(
        "event_sponsors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("sponsor_id", sa.Integer(), nullable=False),
        sa.Column("tier", sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"]),
        sa.ForeignKeyConstraint(["sponsor_id"], ["sponsors.id"]),
    )
    op.create_index(op.f("ix_event_sponsors_event_id"), "event_sponsors", ["event_id"], unique=False)
    op.create_index(op.f("ix_event_sponsors_sponsor_id"), "event_sponsors", ["sponsor_id"], unique=False)

    op.create_table(
        "event_materials",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=128), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("stored_path", sa.String(length=512), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"]),
    )
    op.create_index(op.f("ix_event_materials_event_id"), "event_materials", ["event_id"], unique=False)

    op.create_table(
        "event_registrations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("registered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("checked_in_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"]),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"]),
        sa.UniqueConstraint("event_id", "student_id", name="uq_event_student"),
    )
    op.create_index(op.f("ix_event_registrations_event_id"), "event_registrations", ["event_id"], unique=False)
    op.create_index(op.f("ix_event_registrations_student_id"), "event_registrations", ["student_id"], unique=False)
    op.create_index(op.f("ix_event_registrations_status"), "event_registrations", ["status"], unique=False)

    op.create_table(
        "waiting_list_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"]),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"]),
        sa.UniqueConstraint("event_id", "student_id", name="uq_waiting_event_student"),
    )
    op.create_index(op.f("ix_waiting_list_entries_event_id"), "waiting_list_entries", ["event_id"], unique=False)
    op.create_index(op.f("ix_waiting_list_entries_student_id"), "waiting_list_entries", ["student_id"], unique=False)

    op.create_table(
        "tickets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("registration_id", sa.Integer(), nullable=False),
        sa.Column("qr_payload", sa.String(length=512), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("checked_in_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["registration_id"], ["event_registrations.id"]),
        sa.UniqueConstraint("registration_id"),
        sa.UniqueConstraint("qr_payload"),
    )
    op.create_index(op.f("ix_tickets_registration_id"), "tickets", ["registration_id"], unique=False)
    op.create_index(op.f("ix_tickets_qr_payload"), "tickets", ["qr_payload"], unique=False)

    op.create_table(
        "feedback",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("sentiment_label", sa.String(length=32), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"]),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"]),
        sa.UniqueConstraint("event_id", "student_id", name="uq_feedback_event_student"),
    )
    op.create_index(op.f("ix_feedback_event_id"), "feedback", ["event_id"], unique=False)
    op.create_index(op.f("ix_feedback_student_id"), "feedback", ["student_id"], unique=False)

    op.create_table(
        "favorite_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"]),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"]),
        sa.UniqueConstraint("event_id", "student_id", name="uq_fav_event_student"),
    )
    op.create_index(op.f("ix_favorite_events_event_id"), "favorite_events", ["event_id"], unique=False)
    op.create_index(op.f("ix_favorite_events_student_id"), "favorite_events", ["student_id"], unique=False)

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=64), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index(op.f("ix_notifications_user_id"), "notifications", ["user_id"], unique=False)
    op.create_index(op.f("ix_notifications_type"), "notifications", ["type"], unique=False)

    op.create_table(
        "reminders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index(op.f("ix_reminders_user_id"), "reminders", ["user_id"], unique=False)
    op.create_index(op.f("ix_reminders_event_id"), "reminders", ["event_id"], unique=False)

    op.create_table(
        "reports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("type", sa.String(length=64), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("file_path", sa.String(length=512), nullable=True),
    )
    op.create_index(op.f("ix_reports_type"), "reports", ["type"], unique=False)

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("actor_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=128), nullable=False),
        sa.Column("entity_type", sa.String(length=64), nullable=True),
        sa.Column("entity_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("details_json", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"]),
    )
    op.create_index(op.f("ix_audit_logs_actor_id"), "audit_logs", ["actor_id"], unique=False)
    op.create_index(op.f("ix_audit_logs_action"), "audit_logs", ["action"], unique=False)

    op.create_table(
        "scraped_event_drafts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("raw_payload_json", sa.Text(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("start_dt", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_dt", sa.DateTime(timezone=True), nullable=False),
        sa.Column("location_text", sa.String(length=255), nullable=True),
        sa.Column("category_text", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("approved_by_admin_id", sa.Integer(), nullable=True),
        sa.Column("approved_event_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["approved_by_admin_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["approved_event_id"], ["events.id"]),
    )
    op.create_index(op.f("ix_scraped_event_drafts_source"), "scraped_event_drafts", ["source"], unique=False)
    op.create_index(op.f("ix_scraped_event_drafts_status"), "scraped_event_drafts", ["status"], unique=False)
    op.create_index(op.f("ix_scraped_event_drafts_title"), "scraped_event_drafts", ["title"], unique=False)
    op.create_index(op.f("ix_scraped_event_drafts_start_dt"), "scraped_event_drafts", ["start_dt"], unique=False)
    op.create_index(op.f("ix_scraped_event_drafts_end_dt"), "scraped_event_drafts", ["end_dt"], unique=False)


def downgrade() -> None:
    op.drop_table("scraped_event_drafts")
    op.drop_table("audit_logs")
    op.drop_table("reports")
    op.drop_table("reminders")
    op.drop_table("notifications")
    op.drop_table("favorite_events")
    op.drop_table("feedback")
    op.drop_table("tickets")
    op.drop_table("waiting_list_entries")
    op.drop_table("event_registrations")
    op.drop_table("event_materials")
    op.drop_table("event_sponsors")
    op.drop_table("sponsors")
    op.drop_table("events")
    op.drop_table("organizer_profiles")
    op.drop_table("student_profiles")
    op.drop_table("locations")
    op.drop_table("faculty_departments")
    op.drop_table("event_categories")
    op.drop_table("users")
    op.drop_table("roles")

