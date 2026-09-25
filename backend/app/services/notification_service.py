from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import notification as crud_notification
from app.models.notification import Notification


class NotificationService:
    async def get_notification_or_404(
        self, db: AsyncSession, notification_id: int
    ) -> Notification:
        notification = await crud_notification.get_notification_by_id(
            db, notification_id
        )
        if not notification:
            raise HTTPException(
                status_code=404, detail="Notification not found"
            )
        return notification

    async def get_notifications(
        self, db: AsyncSession, user_id: int, is_read: bool | None = None
    ):
        return await crud_notification.get_notifications(db, user_id, is_read)

    async def mark_as_read(
        self, db: AsyncSession, notification_id: int, user_id: int
    ) -> Notification:
        notification = await self.get_notification_or_404(db, notification_id)
        if notification.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        return await crud_notification.mark_as_read(db, notification)

    async def mark_all_as_read(self, db: AsyncSession, user_id: int) -> int:
        return await crud_notification.mark_all_as_read(db, user_id)

    async def create_notification(
        self, db: AsyncSession, user_id: int, message: str
    ) -> Notification:
        return await crud_notification.create_notification(
            db, user_id, message
        )


notification_service = NotificationService()
