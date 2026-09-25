from typing import Optional, Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col

from app.models.notification import Notification


async def get_notification_by_id(
    db: AsyncSession, notification_id: int
) -> Optional[Notification]:
    result = await db.execute(
        select(Notification).where(col(Notification.id) == notification_id)
    )
    return result.scalars().first()


async def get_notifications(
    db: AsyncSession,
    user_id: int,
    is_read: Optional[bool] = None,
) -> Sequence[Notification]:
    query = select(Notification).where(col(Notification.user_id) == user_id)
    if is_read is not None:
        query = query.where(col(Notification.is_read).is_(is_read))
    result = await db.execute(query)
    return result.scalars().all()


async def mark_as_read(
    db: AsyncSession, notification: Notification
) -> Notification:
    notification.is_read = True
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    return notification


async def mark_all_as_read(db: AsyncSession, user_id: int) -> int:
    result = await db.execute(
        update(Notification)
        .where(col(Notification.user_id) == user_id)
        .where(col(Notification.is_read).is_(False))
        .values(is_read=True)
    )
    await db.commit()
    return result.rowcount


async def create_notification(
    db: AsyncSession, user_id: int, message: str
) -> Notification:
    notification = Notification(user_id=user_id, message=message)
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    return notification
