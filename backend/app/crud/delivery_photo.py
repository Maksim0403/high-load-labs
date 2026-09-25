from typing import Any, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.delivery_photo import DeliveryPhoto


async def get_photos_by_route(
    db: AsyncSession, route_id: int
) -> Sequence[Any]:
    result = await db.execute(
        select(DeliveryPhoto).where(DeliveryPhoto.route_id == route_id)
    )
    return result.scalars().all()


async def create_photo(
    db: AsyncSession, route_id: int, key: str, description: str | None
) -> DeliveryPhoto:
    db_photo = DeliveryPhoto(
        route_id=route_id, key=key, description=description
    )
    db.add(db_photo)
    await db.commit()
    await db.refresh(db_photo)
    return db_photo


async def get_photo_by_id(
    db: AsyncSession, photo_id: int
) -> DeliveryPhoto | None:
    result = await db.execute(
        select(DeliveryPhoto).where(DeliveryPhoto.id == photo_id)
    )
    return result.scalar_one_or_none()


async def delete_photo(db: AsyncSession, db_photo: DeliveryPhoto) -> None:
    await db.delete(db_photo)
    await db.commit()
