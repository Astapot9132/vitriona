"""add refresh token hash to sessions"""

from alembic import op
import sqlalchemy as sa


revision = "2026_04_19_000002"
down_revision = "2026_04_17_000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("sessions", sa.Column("refresh_token_hash", sa.String(length=64), nullable=True))


def downgrade() -> None:
    op.drop_column("sessions", "refresh_token_hash")
