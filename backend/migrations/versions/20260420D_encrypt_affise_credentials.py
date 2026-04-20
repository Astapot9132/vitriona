"""encrypt affise credentials"""

from alembic import op
import sqlalchemy as sa
from cryptography.fernet import Fernet

from cfg import AFFISE_DATA_SECRET


revision = "20260420D"
down_revision = "20260420C"
branch_labels = None
depends_on = None


def _cipher() -> Fernet:
    return Fernet(AFFISE_DATA_SECRET.encode("utf-8"))


def upgrade() -> None:
    op.alter_column("users", "affise_password", existing_type=sa.String(length=255), type_=sa.Text(), existing_nullable=True)
    op.alter_column("users", "affise_api_key", existing_type=sa.String(length=255), type_=sa.Text(), existing_nullable=True)

    bind = op.get_bind()
    cipher = _cipher()
    rows = bind.execute(
        sa.text(
            """
            SELECT id, affise_password, affise_api_key
            FROM users
            WHERE affise_password IS NOT NULL OR affise_api_key IS NOT NULL
            """
        )
    ).mappings()

    for row in rows:
        affise_password = row["affise_password"]
        affise_api_key = row["affise_api_key"]
        bind.execute(
            sa.text(
                """
                UPDATE users
                SET affise_password = :affise_password,
                    affise_api_key = :affise_api_key
                WHERE id = :user_id
                """
            ),
            {
                "user_id": row["id"],
                "affise_password": cipher.encrypt(affise_password.encode("utf-8")).decode("utf-8") if affise_password else None,
                "affise_api_key": cipher.encrypt(affise_api_key.encode("utf-8")).decode("utf-8") if affise_api_key else None,
            },
        )


def downgrade() -> None:
    bind = op.get_bind()
    cipher = _cipher()
    rows = bind.execute(
        sa.text(
            """
            SELECT id, affise_password, affise_api_key
            FROM users
            WHERE affise_password IS NOT NULL OR affise_api_key IS NOT NULL
            """
        )
    ).mappings()

    for row in rows:
        affise_password = row["affise_password"]
        affise_api_key = row["affise_api_key"]
        bind.execute(
            sa.text(
                """
                UPDATE users
                SET affise_password = :affise_password,
                    affise_api_key = :affise_api_key
                WHERE id = :user_id
                """
            ),
            {
                "user_id": row["id"],
                "affise_password": cipher.decrypt(affise_password.encode("utf-8")).decode("utf-8") if affise_password else None,
                "affise_api_key": cipher.decrypt(affise_api_key.encode("utf-8")).decode("utf-8") if affise_api_key else None,
            },
        )

    op.alter_column("users", "affise_api_key", existing_type=sa.Text(), type_=sa.String(length=255), existing_nullable=True)
    op.alter_column("users", "affise_password", existing_type=sa.Text(), type_=sa.String(length=255), existing_nullable=True)
