from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import (
    Column,
    DateTime,
    Enum,
    Field,
    Relationship,
    SQLModel,
    func,
)

from app.enums import UserRole

if TYPE_CHECKING:
    from app.models.order import Order
    from app.models.vehicle import Vehicle


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, nullable=False)
    hashed_password: str = Field(nullable=False)

    role: UserRole = Field(
        sa_column=Column(Enum(UserRole, native_enum=False), nullable=False)
    )

    full_name: Optional[str] = None
    phone_number: str = Field(unique=True, index=True, nullable=False)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )

    orders: List["Order"] = Relationship(back_populates="owner")

    vehicle: Optional["Vehicle"] = Relationship(back_populates="driver")
