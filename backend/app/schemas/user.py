from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.enums import UserRole
from app.schemas.vehicle import VehicleOut


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole
    phone_number: str = Field(
        ..., json_schema_extra={"example": "+380991234567"}
    )


class UserLogin(BaseModel):
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: UserRole
    full_name: str
    phone_number: str
    created_at: datetime
    vehicle: Optional[VehicleOut] = None

    model_config = ConfigDict(from_attributes=True)
