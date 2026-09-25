from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Enum, Numeric
from sqlmodel import Column, DateTime, Field, Relationship, SQLModel, func

from app.enums import OrderStatus

if TYPE_CHECKING:
    from app.models.user import User


class Order(SQLModel, table=True):
    __tablename__ = "orders"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    origin_address: Optional[str] = Field(default=None)
    destination_address: Optional[str] = Field(default=None)
    weight: float = Field(nullable=False)
    distance: float = Field(nullable=False)
    status: OrderStatus = Field(
        sa_column=Column(
            Enum(OrderStatus, native_enum=False),
            nullable=False,
            server_default=OrderStatus.PENDING,
        ),
        default=OrderStatus.PENDING,
    )

    owner_id: int = Field(foreign_key="users.id", nullable=False)
    is_template: bool = Field(default=False, nullable=False)
    total_amount: float = Field(
        sa_column=Column(Numeric(10, 2), default=0.0, nullable=False),
        default=0.0,
    )

    owner: Optional["User"] = Relationship(back_populates="orders")

    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    received_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )
