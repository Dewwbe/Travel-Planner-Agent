"""Add Calendar OAuth, agent memory, and pending actions.

Revision ID: 002_calendar_memory
Revises: 001_initial
"""

from alembic import op
import sqlalchemy as sa


revision = "002_calendar_memory"
down_revision = "001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "calendar_credentials",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("encrypted_token", sa.LargeBinary(), nullable=False),
        sa.Column("scopes", sa.Text(), nullable=False),
        sa.Column(
            "provider",
            sa.String(length=30),
            server_default="google",
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "user_id",
            name="uq_calendar_credentials_user_id",
        ),
    )

    op.create_index(
        "ix_calendar_credentials_user_id",
        "calendar_credentials",
        ["user_id"],
    )

    op.create_table(
        "user_memories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column("value", sa.JSON(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "user_id",
            "key",
            name="uq_user_memory_key",
        ),
    )

    op.create_index(
        "ix_user_memories_user_id",
        "user_memories",
        ["user_id"],
    )

    op.create_table(
        "pending_actions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "trip_id",
            sa.Integer(),
            sa.ForeignKey("trips.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("thread_id", sa.String(length=100), nullable=False),
        sa.Column("action_type", sa.String(length=50), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column(
            "status",
            sa.String(length=30),
            server_default="pending",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "executed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_pending_actions_user_id",
        "pending_actions",
        ["user_id"],
    )
    op.create_index(
        "ix_pending_actions_trip_id",
        "pending_actions",
        ["trip_id"],
    )
    op.create_index(
        "ix_pending_actions_thread_id",
        "pending_actions",
        ["thread_id"],
    )
    op.create_index(
        "ix_pending_actions_status",
        "pending_actions",
        ["status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_pending_actions_status",
        table_name="pending_actions",
    )
    op.drop_index(
        "ix_pending_actions_thread_id",
        table_name="pending_actions",
    )
    op.drop_index(
        "ix_pending_actions_trip_id",
        table_name="pending_actions",
    )
    op.drop_index(
        "ix_pending_actions_user_id",
        table_name="pending_actions",
    )
    op.drop_table("pending_actions")

    op.drop_index(
        "ix_user_memories_user_id",
        table_name="user_memories",
    )
    op.drop_table("user_memories")

    op.drop_index(
        "ix_calendar_credentials_user_id",
        table_name="calendar_credentials",
    )
    op.drop_table("calendar_credentials")