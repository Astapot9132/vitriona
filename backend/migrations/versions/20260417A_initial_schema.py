"""initial schema"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260417A"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_banned", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("affise_password", sa.String(length=255), nullable=True),
        sa.Column("affise_country", sa.String(length=2), nullable=True),
        sa.Column("affise_id", sa.BigInteger(), nullable=True),
        sa.Column("affise_api_key", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=False)

    op.create_table(
        "pin_codes",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("code_hash", sa.String(length=255), nullable=False),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("attempts", sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_pin_codes_email", "pin_codes", ["email"], unique=False)

    op.create_table(
        "offer_sources",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("type", sa.String(length=64), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("name", name="uq_offer_sources_name"),
    )

    op.create_table(
        "sessions",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("csrf_token", sa.Text(), nullable=False),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("impersonator_admin_id", sa.BigInteger(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_sessions_user_id", "sessions", ["user_id"], unique=False)

    op.create_table(
        "offers",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("source_id", sa.BigInteger(), sa.ForeignKey("offer_sources.id", ondelete="CASCADE"), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False, server_default="active"),
        sa.Column("privacy", sa.String(length=64), nullable=False, server_default="public"),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("preview_url", sa.Text(), nullable=True),
        sa.Column("logo", sa.String(length=1024), nullable=True),
        sa.Column("description_lang", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("categories", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("countries", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("payments", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("targeting", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("cr", sa.Float(), nullable=False, server_default="0"),
        sa.Column("epc", sa.Float(), nullable=False, server_default="0"),
        sa.Column("hold_period", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("raw_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("external_created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("external_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("source_id", "external_id", name="uq_offers_source_external"),
    )
    op.create_index("ix_offers_source_id", "offers", ["source_id"], unique=False)
    op.create_index("ix_offers_status", "offers", ["status"], unique=False)

    op.create_table(
        "showcases",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("platform_main", sa.String(length=255), nullable=False),
        sa.Column("platform_sub", sa.String(length=255), nullable=True),
        sa.Column("url", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False, server_default="draft"),
        sa.Column("config", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_showcases_user_id", "showcases", ["user_id"], unique=False)

    op.create_table(
        "domains",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("system_domain", sa.String(length=255), nullable=False),
        sa.Column("webmaster_domain", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False, server_default="pending"),
        sa.Column("admin_comment", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_domains_user_id", "domains", ["user_id"], unique=False)

    op.create_table(
        "partner_offers",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("external_id", sa.BigInteger(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("logo", sa.String(length=1024), nullable=False, server_default=""),
        sa.Column("preview_url", sa.String(length=1024), nullable=False, server_default=""),
        sa.Column("link", sa.Text(), nullable=False, server_default=""),
        sa.Column("description_lang", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("categories", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("countries", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("payments", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("targeting", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("sources", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("landings", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("cr", sa.Float(), nullable=False, server_default="0"),
        sa.Column("epc", sa.Float(), nullable=False, server_default="0"),
        sa.Column("hold_period", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("required_approval", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("raw_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("user_id", "external_id", name="uq_partner_offers_user_external"),
    )
    op.create_index("ix_partner_offers_user_id", "partner_offers", ["user_id"], unique=False)

    op.execute(
        """
        INSERT INTO offer_sources (name, type, enabled, created_at, updated_at)
        VALUES ('Affise Sync', 'affise', true, now(), now())
        """
    )


def downgrade() -> None:
    op.drop_table("partner_offers")
    op.drop_table("domains")
    op.drop_table("showcases")
    op.drop_table("offers")
    op.drop_table("sessions")
    op.drop_table("offer_sources")
    op.drop_table("pin_codes")
    op.drop_table("users")
