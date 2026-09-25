from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DeliveryPhotoCreate(BaseModel):
    description: Optional[str] = Field(default=None, max_length=255)


class DeliveryPhotoOut(BaseModel):
    id: int
    route_id: int
    key: str
    description: Optional[str]
    taken: datetime

    model_config = ConfigDict(from_attributes=True)


class DeliveryPhotoUploadOut(BaseModel):
    key: str
    url: str
