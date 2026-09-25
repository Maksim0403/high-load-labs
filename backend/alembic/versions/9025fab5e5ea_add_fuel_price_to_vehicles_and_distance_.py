"""add fuel price to vehicles and distance to orders

Revision ID: 9025fab5e5ea
Revises: 4103e81c4c65
Create Date: 2026-06-04 16:30:05.720115

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "9025fab5e5ea"
down_revision: Union[str, Sequence[str], None] = "4103e81c4c65"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "vehicles",
        sa.Column(
            "fuel_price", sa.Float(), nullable=False, server_default="0"
        ),
    )

    op.add_column(
        "orders",
        sa.Column("distance", sa.Float(), nullable=False, server_default="0"),
    )

    op.drop_column("routes", "distance")


def downgrade() -> None:
    op.add_column("routes", sa.Column("distance", sa.Float(), nullable=True))
    op.drop_column("orders", "distance")
    op.drop_column("vehicles", "fuel_price")
