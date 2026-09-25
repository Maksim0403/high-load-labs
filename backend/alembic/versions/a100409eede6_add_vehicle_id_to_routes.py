"""add vehicle_id to routes

Revision ID: a100409eede6
Revises: 9025fab5e5ea
Create Date: 2026-06-04 16:55:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "a100409eede6"
down_revision: Union[str, Sequence[str], None] = "9025fab5e5ea"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "routes",
        sa.Column(
            "vehicle_id",
            sa.Integer(),
            sa.ForeignKey("vehicles.id"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("routes", "vehicle_id")
