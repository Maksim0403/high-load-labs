"""initial_migration and update roles

Revision ID: a283d016c91f
Revises:
Create Date: 2026-04-21 21:11:29.169773

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel

from alembic import op

revision: str = "a283d016c91f"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "hashed_password",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=False,
        ),
        sa.Column(
            "role",
            sa.Enum(
                "CLIENT",
                "DRIVER",
                "MANAGER",
                name="userrole",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "full_name", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
        sa.Column(
            "phone_number", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_users_email"), ["email"], unique=True
        )
        batch_op.create_index(
            batch_op.f("ix_users_phone_number"), ["phone_number"], unique=True
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_users_phone_number"))
        batch_op.drop_index(batch_op.f("ix_users_email"))

    op.drop_table("users")
