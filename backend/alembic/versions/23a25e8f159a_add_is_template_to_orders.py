"""add is_template to orders

Revision ID: 23a25e8f159a
Revises: 527515046fad
Create Date: 2026-05-12 14:27:13.175243

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "23a25e8f159a"
down_revision: Union[str, Sequence[str], None] = "527515046fad"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "orders",
        sa.Column(
            "is_template",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("orders", "is_template")
