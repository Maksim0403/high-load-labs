"""merge_heads

Revision ID: 9e8f127d1f23
Revises: 52576e5c4ec9, a100409eede6
Create Date: 2026-06-12 00:40:54.349411

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9e8f127d1f23'
down_revision: Union[str, Sequence[str], None] = ('52576e5c4ec9', 'a100409eede6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
