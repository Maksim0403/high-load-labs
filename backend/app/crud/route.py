from datetime import date
from typing import Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlmodel import col

from app.models.route import Route
from app.schemas.route import RouteCreate, RouteUpdate


async def get_route_by_id(db: AsyncSession, route_id: int) -> Optional[Route]:
    result = await db.execute(
        select(Route)
        .where(col(Route.id) == route_id)
        .options(joinedload(Route.order))
    )
    return result.scalars().first()


async def get_route_by_order_id(
    db: AsyncSession, order_id: int
) -> Optional[Route]:
    result = await db.execute(
        select(Route)
        .where(col(Route.order_id) == order_id)
        .options(joinedload(Route.order))
    )
    return result.scalars().first()


async def get_routes(
    db: AsyncSession,
    driver_id: Optional[int] = None,
    order_id: Optional[int] = None,
) -> Sequence[Route]:
    query = select(Route).options(joinedload(Route.order))
    if driver_id is not None:
        query = query.where(col(Route.driver_id) == driver_id)
    if order_id is not None:
        query = query.where(col(Route.order_id) == order_id)
    result = await db.execute(query)
    return result.scalars().all()


async def get_today_routes_by_driver(
    db: AsyncSession, driver_id: int
) -> Sequence[Route]:
    today = date.today()
    query = (
        select(Route)
        .where(
            col(Route.driver_id) == driver_id,
            func.date(Route.eta) == today,
        )
        .options(joinedload(Route.order))
    )
    result = await db.execute(query)
    return result.scalars().all()


async def create_route(db: AsyncSession, route_in: RouteCreate) -> Route:
    db_route = Route(
        order_id=route_in.order_id,
        driver_id=route_in.driver_id,
        eta=route_in.eta,
    )
    db.add(db_route)
    await db.commit()
    await db.refresh(db_route)

    await db.execute(
        select(Route)
        .where(Route.id == db_route.id)
        .options(joinedload(Route.order))
    )
    return db_route


async def update_route(
    db: AsyncSession, route: Route, route_in: RouteUpdate
) -> Route:
    update_data = route_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(route, field, value)
    db.add(route)
    await db.commit()
    await db.refresh(route)

    await db.execute(
        select(Route)
        .where(Route.id == route.id)
        .options(joinedload(Route.order))
    )
    return route


async def delete_route(db: AsyncSession, route: Route) -> None:
    await db.delete(route)
    await db.commit()
