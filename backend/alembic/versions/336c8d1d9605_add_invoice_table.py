"""add invoice table

Revision ID: 336c8d1d9605
Revises: 23a25e8f159a
Create Date: 2026-05-13 17:09:33.663095

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "336c8d1d9605"
down_revision: Union[str, Sequence[str], None] = "23a25e8f159a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "invoices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=True),
        sa.Column("billing_month", sa.DateTime(timezone=True), nullable=False),
        sa.Column("total_shipment", sa.Integer(), nullable=False),
        sa.Column(
            "total_weight", sa.Numeric(precision=10, scale=2), nullable=True
        ),
        sa.Column(
            "total_volume", sa.Numeric(precision=10, scale=3), nullable=True
        ),
        sa.Column(
            "total_distance", sa.Numeric(precision=10, scale=2), nullable=True
        ),
        sa.Column(
            "generated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("invoices")
