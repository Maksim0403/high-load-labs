from datetime import datetime
from typing import Optional

from sqlmodel import Column, DateTime, Enum, Field, SQLModel, func

from app.enums import RouteStatusEnum


class RouteStatus(SQLModel, table=True):
    __tablename__ = "route_statuses"

    id: Optional[int] = Field(default=None, primary_key=True)

    route_id: int = Field(foreign_key="routes.id", nullable=False)
    status: RouteStatusEnum = Field(
        sa_column=Column(
            Enum(RouteStatusEnum, native_enum=False), nullable=False
        )
    )
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
