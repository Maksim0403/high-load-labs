from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Column, DateTime, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.delivery_photo import DeliveryPhoto
    from app.models.order import Order
    from app.models.vehicle import Vehicle


class Route(SQLModel, table=True):
    __tablename__ = "routes"

    id: Optional[int] = Field(default=None, primary_key=True)

    order_id: int = Field(foreign_key="orders.id", nullable=False)
    driver_id: Optional[int] = Field(default=None, foreign_key="users.id")
    vehicle_id: Optional[int] = Field(default=None, foreign_key="vehicles.id")

    started_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    eta: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    completed_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )

    fuel_cost: Optional[float] = Field(default=None)

    order: "Order" = Relationship()
    vehicle: Optional["Vehicle"] = Relationship()
    photos: List["DeliveryPhoto"] = Relationship(back_populates="route")
