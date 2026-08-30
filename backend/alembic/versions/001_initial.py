"""Initial user and trip tables."""
from alembic import op
import sqlalchemy as sa

revision = "001_initial"
down_revision = None

def upgrade():
    op.create_table("users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_table("trips",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("destination", sa.String(120), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("budget", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(3), server_default="USD", nullable=False),
        sa.Column("status", sa.String(30), server_default="draft", nullable=False),
        sa.Column("request_text", sa.Text(), nullable=True),
        sa.Column("itinerary", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_trips_user_id", "trips", ["user_id"])

def downgrade():
    op.drop_table("trips")
    op.drop_table("users")

