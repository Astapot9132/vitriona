"""add refresh token hash to sessions"""

from alembic import op
import sqlalchemy as sa


revision = "20260419A"
down_revision = "20260417A"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("sessions", sa.Column("refresh_token_hash", sa.String(length=64), nullable=True))


def downgrade() -> None:
    op.drop_column("sessions", "refresh_token_hash")
