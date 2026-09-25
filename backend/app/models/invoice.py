from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, DateTime, Numeric
from sqlmodel import Field, Relationship, SQLModel, func

if TYPE_CHECKING:
    from app.models.user import User


class Invoice(SQLModel, table=True):
    __tablename__ = "invoices"

    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: Optional[int] = Field(default=None, foreign_key="users.id")

    billing_month: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )

    total_shipment: int = Field(default=0)

    total_weight: float = Field(sa_column=Column(Numeric(10, 2), default=0.0))

    total_volume: float = Field(sa_column=Column(Numeric(10, 3), default=0.0))

    total_distance: float = Field(
        sa_column=Column(Numeric(10, 2), default=0.0)
    )

    total_amount: float = Field(
        sa_column=Column(Numeric(10, 2), default=0.0, nullable=False),
        default=0.0,
    )

    generated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )

    owner: Optional["User"] = Relationship()
