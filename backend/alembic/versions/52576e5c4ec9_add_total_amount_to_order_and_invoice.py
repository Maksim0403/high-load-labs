"""add_total_amount_to_order_and_invoice

Revision ID: 52576e5c4ec9
Revises: 358021460daa
Create Date: 2026-06-02 16:07:03.697076

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "52576e5c4ec9"
down_revision: Union[str, Sequence[str], None] = "358021460daa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "invoices",
        sa.Column(
            "total_amount", sa.Numeric(precision=10, scale=2), nullable=True
        ),
    )
    op.add_column(
        "orders",
        sa.Column(
            "total_amount", sa.Numeric(precision=10, scale=2), nullable=True
        ),
    )

    op.execute("UPDATE invoices SET total_amount = 0.0")
    op.execute("UPDATE orders SET total_amount = 0.0")

    op.alter_column("invoices", "total_amount", nullable=False)
    op.alter_column("orders", "total_amount", nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("orders", "total_amount")
    op.drop_column("invoices", "total_amount")
