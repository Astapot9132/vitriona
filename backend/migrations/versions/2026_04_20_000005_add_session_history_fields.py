"""add session history fields"""

from alembic import op
import sqlalchemy as sa


revision = "2026_04_20_000005"
down_revision = "2026_04_20_000004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("sessions", sa.Column("is_closed", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("sessions", sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("sessions", sa.Column("close_reason", sa.String(length=64), nullable=True))
    op.add_column("sessions", sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True))
    op.alter_column("sessions", "is_closed", server_default=None)


def downgrade() -> None:
    op.drop_column("sessions", "last_seen_at")
    op.drop_column("sessions", "close_reason")
    op.drop_column("sessions", "closed_at")
    op.drop_column("sessions", "is_closed")
