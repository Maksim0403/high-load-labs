"""add addresses to orders

Revision ID: 3104cacec322
Revises: acd8e4bef2dd
Create Date: 2026-05-14 13:04:24.909562

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "3104cacec322"
down_revision: Union[str, Sequence[str], None] = "acd8e4bef2dd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "orders", sa.Column("origin_address", sa.String(), nullable=True)
    )
    op.add_column(
        "orders", sa.Column("destination_address", sa.String(), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("orders", "destination_address")
    op.drop_column("orders", "origin_address")
