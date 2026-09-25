"""add distance and fuel_cost to routes

Revision ID: 4103e81c4c65
Revises: 358021460daa
Create Date: 2026-06-04 14:03:04.272954

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "4103e81c4c65"
down_revision: Union[str, Sequence[str], None] = "358021460daa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("routes", schema=None) as batch_op:
        batch_op.add_column(sa.Column("distance", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("fuel_cost", sa.Float(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("routes", schema=None) as batch_op:
        batch_op.drop_column("fuel_cost")
        batch_op.drop_column("distance")
