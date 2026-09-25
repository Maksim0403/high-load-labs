"""add invoices table

Revision ID: acd8e4bef2dd
Revises: 336c8d1d9605
Create Date: 2026-05-14 11:02:58.327960

"""

from typing import Sequence, Union

revision: str = "acd8e4bef2dd"
down_revision: Union[str, Sequence[str], None] = "336c8d1d9605"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
