from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col

from app.models.route_status import RouteStatus
from app.schemas.route_status import RouteStatusCreate


async def get_statuses_by_route_id(
    db: AsyncSession, route_id: int
) -> Sequence[RouteStatus]:
    result = await db.execute(
        select(RouteStatus)
        .where(col(RouteStatus.route_id) == route_id)
        .order_by(RouteStatus.created_at)
    )
    return result.scalars().all()


async def get_latest_status(
    db: AsyncSession, route_id: int
) -> Optional[RouteStatus]:
    result = await db.execute(
        select(RouteStatus)
        .where(col(RouteStatus.route_id) == route_id)
        .order_by(col(RouteStatus.created_at).desc())
        .limit(1)
    )
    return result.scalars().first()


async def create_route_status(
    db: AsyncSession, route_id: int, status_in: RouteStatusCreate
) -> RouteStatus:
    db_status = RouteStatus(
        route_id=route_id,
        status=status_in.status,
    )
    db.add(db_status)
    await db.commit()
    await db.refresh(db_status)
    return db_status
