"""add all tables

Revision ID: 44cb2df47560
Revises: 04fd39533d08
Create Date: 2026-04-23 23:45:28.334119

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel

from alembic import op

revision: str = "44cb2df47560"
down_revision: Union[str, Sequence[str], None] = "a283d016c91f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "message",
            sqlmodel.sql.sqltypes.AutoString(length=255),
            nullable=False,
        ),
        sa.Column("is_read", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "description", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "PENDING",
                "IN_PROGRESS",
                "COMPLETED",
                "CANCELED",
                name="orderstatus",
                native_enum=False,
            ),
            server_default="pending",
            nullable=False,
        ),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "routes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("driver_id", sa.Integer(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("eta", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["driver_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["orders.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "shipments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("weight", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("volume", sa.Numeric(precision=10, scale=3), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column(
            "description",
            sqlmodel.sql.sqltypes.AutoString(length=255),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["orders.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "route_statuses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("route_id", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "ASSIGNED",
                "LOADED",
                "IN_TRANSIT",
                "DELIVERED",
                "FAILED",
                name="routestatusenum",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "created_at",
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
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("route_statuses")
    op.drop_table("shipments")
    op.drop_table("routes")
    op.drop_table("orders")
    op.drop_table("notifications")
