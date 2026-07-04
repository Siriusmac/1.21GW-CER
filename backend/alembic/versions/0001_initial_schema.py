"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-07-04
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "communities",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("primary_substation", sa.String(120), nullable=False),
        sa.Column("benefit_rule", sa.String(80), nullable=False, server_default="proportional_consumption"),
    )
    op.create_table(
        "members",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("community_id", sa.String(), sa.ForeignKey("communities.id"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("benefit_share_percent", sa.Float(), nullable=True),
    )
    op.create_table(
        "pods",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("member_id", sa.String(), sa.ForeignKey("members.id"), nullable=False),
        sa.Column("code", sa.String(80), nullable=False, unique=True),
        sa.Column("direction_type", sa.String(30), nullable=False),
    )
    op.create_table(
        "plants",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("member_id", sa.String(), sa.ForeignKey("members.id"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("capacity_kw", sa.Float(), nullable=False),
        sa.Column("pod_id", sa.String(), sa.ForeignKey("pods.id"), nullable=True),
    )
    op.create_table(
        "energy_readings",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column("pod_id", sa.String(), sa.ForeignKey("pods.id"), nullable=False, index=True),
        sa.Column("energy_kwh", sa.Float(), nullable=False),
        sa.Column("direction", sa.String(30), nullable=False, index=True),
        sa.Column("source", sa.String(80), nullable=False, server_default="csv"),
        sa.Column("validated", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_table("energy_readings")
    op.drop_table("plants")
    op.drop_table("pods")
    op.drop_table("members")
    op.drop_table("communities")
