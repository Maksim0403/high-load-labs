"""add received_at to orders

Revision ID: 358021460daa
Revises: 3104cacec322
Create Date: 2026-05-26 13:03:28.562927

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "358021460daa"
down_revision: Union[str, Sequence[str], None] = "3104cacec322"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("orders", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("received_at", sa.DateTime(timezone=True), nullable=True)
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("orders", schema=None) as batch_op:
        batch_op.drop_column("received_at")
