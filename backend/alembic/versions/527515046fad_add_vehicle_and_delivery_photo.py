"""add vehicle and delivery photo

Revision ID: 527515046fad
Revises: 44cb2df47560
Create Date: 2026-05-08 11:57:20.850410

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel

from alembic import op

revision: str = "527515046fad"
down_revision: Union[str, Sequence[str], None] = "44cb2df47560"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "vehicles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("driver_id", sa.Integer(), nullable=True),
        sa.Column(
            "brand",
            sqlmodel.sql.sqltypes.AutoString(length=50),
            nullable=False,
        ),
        sa.Column(
            "model",
            sqlmodel.sql.sqltypes.AutoString(length=50),
            nullable=False,
        ),
        sa.Column(
            "license_plate",
            sqlmodel.sql.sqltypes.AutoString(length=8),
            nullable=False,
        ),
        sa.Column("max_weight", sa.Float(), nullable=False),
        sa.Column("max_volume", sa.Float(), nullable=False),
        sa.Column("fuel_consumption", sa.Float(), nullable=False),
        sa.Column("current_mileage", sa.Integer(), nullable=False),
        sa.Column("maintenance_interval", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["driver_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("vehicles", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_vehicles_license_plate"),
            ["license_plate"],
            unique=True,
        )

    op.create_table(
        "delivery_photos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("route_id", sa.Integer(), nullable=False),
        sa.Column(
            "key", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False
        ),
        sa.Column(
            "description",
            sqlmodel.sql.sqltypes.AutoString(length=255),
            nullable=True,
        ),
        sa.Column(
            "taken",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["route_id"],
            ["routes.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("delivery_photos")
    with op.batch_alter_table("vehicles", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_vehicles_license_plate"))

    op.drop_table("vehicles")
