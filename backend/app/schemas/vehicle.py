from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class VehicleCreate(BaseModel):
    brand: str = Field(..., max_length=50)
    model: str = Field(..., max_length=50)
    license_plate: str = Field(
        ..., max_length=8, json_schema_extra={"example": "AA1234BP"}
    )
    max_weight: float = Field(..., gt=0)
    max_volume: float = Field(..., gt=0)
    fuel_consumption: float = Field(..., gt=0)
    fuel_price: float = Field(..., gt=0)
    current_mileage: int = Field(..., ge=0)
    maintenance_interval: int = Field(..., gt=0)


class VehicleUpdate(BaseModel):
    current_mileage: Optional[int] = Field(default=None, ge=0)
    fuel_consumption: Optional[float] = Field(default=None, gt=0)
    fuel_price: Optional[float] = Field(default=None, gt=0)
    maintenance_interval: Optional[int] = Field(default=None, gt=0)


class VehicleOut(BaseModel):
    id: int
    driver_id: Optional[int]
    brand: str
    model: str
    license_plate: str
    max_weight: float
    max_volume: float
    fuel_consumption: float
    fuel_price: float
    current_mileage: int
    maintenance_interval: int

    model_config = ConfigDict(from_attributes=True)
