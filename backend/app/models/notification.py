from datetime import datetime
from typing import Optional

from sqlmodel import Column, DateTime, Field, SQLModel, func


class Notification(SQLModel, table=True):
    __tablename__ = "notifications"

    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="users.id", nullable=False)
    message: str = Field(max_length=255, nullable=False)
    is_read: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
