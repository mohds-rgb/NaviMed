"""portfolio hardening: notes, devices and duty correction support

Revision ID: 6e2a44f12c7b
Revises: 1c4f4903a9f2
"""
from alembic import op
import sqlalchemy as sa

revision = "6e2a44f12c7b"
down_revision = "1c4f4903a9f2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "appointment_notes",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("appointment_id", sa.String(length=36), nullable=False),
        sa.Column("author_user_id", sa.String(length=36), nullable=False),
        sa.Column("note_body", sa.Text(), nullable=False),
        sa.Column("visibility", sa.String(length=24), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["appointment_id"], ["appointments.id"]),
        sa.ForeignKeyConstraint(["author_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_appointment_notes_appointment_id", "appointment_notes", ["appointment_id"], unique=False)
    op.create_index("ix_appointment_notes_author_user_id", "appointment_notes", ["author_user_id"], unique=False)

    op.create_table(
        "device_registrations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("platform", sa.String(length=24), nullable=False),
        sa.Column("push_token", sa.String(length=512), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("push_token"),
    )
    op.create_index("ix_device_registrations_user_id", "device_registrations", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_device_registrations_user_id", table_name="device_registrations")
    op.drop_table("device_registrations")
    op.drop_index("ix_appointment_notes_author_user_id", table_name="appointment_notes")
    op.drop_index("ix_appointment_notes_appointment_id", table_name="appointment_notes")
    op.drop_table("appointment_notes")
