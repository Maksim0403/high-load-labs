from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.enums import OrderStatus


class OrderBase(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=100,
        json_schema_extra={"example": "Доставка будматеріалів"},
    )
    description: Optional[str] = Field(
        None, json_schema_extra={"example": "Привезти 10 мішків цементу"}
    )
    origin_address: Optional[str] = Field(
        None, json_schema_extra={"example": "Київ, вул. Хрещатик, 1"}
    )
    destination_address: Optional[str] = Field(
        None, json_schema_extra={"example": "Львів, вул. Зелена, 10"}
    )
    weight: float = Field(..., gt=0, json_schema_extra={"example": 50.5})
    total_amount: float = Field(
        default=0.0, ge=0, json_schema_extra={"example": 1500.0}
    )
    distance: float = Field(..., gt=0, json_schema_extra={"example": 120.0})
    is_template: bool = Field(default=False)


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    weight: Optional[float] = Field(None, gt=0)
    total_amount: Optional[float] = Field(None, gt=0)
    distance: Optional[float] = Field(None, gt=0)
    status: Optional[OrderStatus] = None
    is_template: Optional[bool] = None
    received_at: Optional[datetime] = None


class OrderAssign(BaseModel):
    driver_id: int
    vehicle_id: int
    eta: datetime


class OrderOut(OrderBase):
    id: int
    owner_id: int
    status: OrderStatus
    created_at: datetime
    received_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
