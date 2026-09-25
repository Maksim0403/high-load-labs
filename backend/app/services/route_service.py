from datetime import datetime, timedelta
from typing import Sequence

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.crud import route as crud_route
from app.enums import UserRole
from app.models.route import Route
from app.schemas.route import RouteCreate, RouteUpdate
from app.services.order_service import order_service
from app.services.user_service import user_service
from app.services.vehicle_service import (
    vehicle_service,
)


class RouteService:
    async def get_route_or_404(self, db: AsyncSession, route_id: int) -> Route:
        route = await crud_route.get_route_by_id(db, route_id)
        if not route:
            raise HTTPException(status_code=404, detail="Route not found")
        return route

    def calculate_eta(self, distance: float, start_time: datetime) -> datetime:
        hours = distance / settings.AVERAGE_SPEED_KMH
        return start_time + timedelta(hours=hours)

    async def get_routes(self, db: AsyncSession, **filters):
        return await crud_route.get_routes(db, **filters)

    async def get_today_routes(
        self, db: AsyncSession, driver_id: int
    ) -> Sequence[Route]:
        return await crud_route.get_today_routes_by_driver(db, driver_id)

    async def create_route(
        self, db: AsyncSession, route_in: RouteCreate
    ) -> Route:
        existing = await crud_route.get_route_by_order_id(
            db, route_in.order_id
        )
        if existing:
            raise HTTPException(
                status_code=409, detail="Route already exists for this order"
            )
        return await crud_route.create_route(db, route_in)

    async def assign_order_to_driver(
        self,
        db: AsyncSession,
        order_id: int,
        driver_id: int,
        vehicle_id: int,
        eta: datetime,
    ) -> Route:

        await order_service.get_order_or_404(db, order_id)

        driver = await user_service.get_user_by_id(db, driver_id)
        if not driver or driver.role != UserRole.DRIVER:
            raise HTTPException(status_code=404, detail="Driver not found")

        vehicle = await vehicle_service.get_vehicle_or_404(db, vehicle_id)
        if vehicle.driver_id != driver_id:
            raise HTTPException(
                status_code=400,
                detail="Vehicle does not belong to this driver",
            )

        existing_route = await crud_route.get_route_by_order_id(db, order_id)
        if existing_route:
            return await crud_route.update_route(
                db,
                existing_route,
                RouteUpdate(
                    driver_id=driver_id, vehicle_id=vehicle_id, eta=eta
                ),
            )

        return await crud_route.create_route(
            db,
            RouteCreate(
                order_id=order_id,
                driver_id=driver_id,
                vehicle_id=vehicle_id,
                eta=eta,
            ),
        )

    async def update_route(
        self, db: AsyncSession, route_id: int, route_in: RouteUpdate
    ) -> Route:
        route = await self.get_route_or_404(db, route_id)
        if route.completed_at is not None:
            raise HTTPException(
                status_code=409, detail="Route is already completed"
            )
        return await crud_route.update_route(db, route, route_in)

    async def delete_route(self, db: AsyncSession, route_id: int) -> None:
        route = await self.get_route_or_404(db, route_id)
        await crud_route.delete_route(db, route)


route_service = RouteService()
