"""add is_admin to users"""

from alembic import op
import sqlalchemy as sa


revision = "2026_04_20_000003"
down_revision = "2026_04_19_000002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )


def downgrade() -> None:
    op.drop_column("users", "is_admin")
