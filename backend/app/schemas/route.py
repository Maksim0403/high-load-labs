from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.order import OrderOut


class RouteCreate(BaseModel):
    order_id: int
    driver_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    eta: datetime


class RouteUpdate(BaseModel):
    driver_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    eta: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    fuel_cost: Optional[float] = None


class RouteOut(BaseModel):
    id: int
    order_id: int
    driver_id: Optional[int]
    vehicle_id: Optional[int] = None
    started_at: Optional[datetime]
    eta: datetime
    completed_at: Optional[datetime]
    fuel_cost: Optional[float] = None
    order: Optional[OrderOut] = None

    model_config = ConfigDict(from_attributes=True)
