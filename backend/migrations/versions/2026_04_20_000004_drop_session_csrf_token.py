"""drop unused session csrf token"""

from alembic import op
import sqlalchemy as sa


revision = "2026_04_20_000004"
down_revision = "2026_04_20_000003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("sessions", "csrf_token")


def downgrade() -> None:
    op.add_column("sessions", sa.Column("csrf_token", sa.Text(), nullable=False, server_default=""))
    op.alter_column("sessions", "csrf_token", server_default=None)
