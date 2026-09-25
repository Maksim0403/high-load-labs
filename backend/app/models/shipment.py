from decimal import Decimal
from typing import Optional

from sqlmodel import Field, SQLModel


class Shipment(SQLModel, table=True):
    __tablename__ = "shipments"

    id: Optional[int] = Field(default=None, primary_key=True)

    order_id: int = Field(foreign_key="orders.id", nullable=False)
    weight: Decimal = Field(max_digits=10, decimal_places=2, nullable=False)
    volume: Decimal = Field(max_digits=10, decimal_places=3, nullable=False)
    quantity: int = Field(nullable=False)
    description: Optional[str] = Field(default=None, max_length=255)
