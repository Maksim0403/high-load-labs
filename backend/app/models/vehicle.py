from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.user import User


class Vehicle(SQLModel, table=True):
    __tablename__ = "vehicles"

    id: Optional[int] = Field(default=None, primary_key=True)
    driver_id: Optional[int] = Field(default=None, foreign_key="users.id")

    brand: str = Field(nullable=False, max_length=50)
    model: str = Field(nullable=False, max_length=50)
    license_plate: str = Field(
        unique=True, index=True, nullable=False, max_length=8
    )

    max_weight: float = Field(nullable=False)
    max_volume: float = Field(nullable=False)
    fuel_consumption: float = Field(nullable=False)
    fuel_price: float = Field(nullable=False)
    current_mileage: int = Field(nullable=False)
    maintenance_interval: int = Field(nullable=False)

    driver: Optional["User"] = Relationship(back_populates="vehicle")
