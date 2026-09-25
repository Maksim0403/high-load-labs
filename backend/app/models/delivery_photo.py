from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Column, DateTime, Field, Relationship, SQLModel, func

if TYPE_CHECKING:
    from app.models.route import Route


class DeliveryPhoto(SQLModel, table=True):
    __tablename__ = "delivery_photos"

    id: Optional[int] = Field(default=None, primary_key=True)
    route_id: int = Field(foreign_key="routes.id", nullable=False)

    key: str = Field(nullable=False, max_length=255)
    description: Optional[str] = Field(default=None, max_length=255)
    taken: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )

    route: Optional["Route"] = Relationship(back_populates="photos")
