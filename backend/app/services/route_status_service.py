from datetime import datetime
from typing import TYPE_CHECKING

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import order as crud_order
from app.crud import route_status as crud_route_status
from app.enums import OrderStatus, RouteStatusEnum
from app.schemas.order import OrderUpdate
from app.schemas.route import RouteUpdate
from app.schemas.route_status import RouteStatusCreate
from app.services.invoice_service import invoice_service
from app.services.route_service import route_service
from app.services.vehicle_service import vehicle_service

if TYPE_CHECKING:
    from app.models.route_status import RouteStatus

ALLOWED_TRANSITIONS: dict[RouteStatusEnum | None, RouteStatusEnum] = {
    None: RouteStatusEnum.ASSIGNED,
    RouteStatusEnum.ASSIGNED: RouteStatusEnum.LOADED,
    RouteStatusEnum.LOADED: RouteStatusEnum.IN_TRANSIT,
    RouteStatusEnum.IN_TRANSIT: RouteStatusEnum.DELIVERED,
}


class RouteStatusService:
    async def get_statuses(self, db: AsyncSession, route_id: int):
        return await crud_route_status.get_statuses_by_route_id(db, route_id)

    async def add_status(
        self,
        db: AsyncSession,
        route_id: int,
        status_in: RouteStatusCreate,
    ) -> "RouteStatus":
        latest = await crud_route_status.get_latest_status(db, route_id)
        current = latest.status if latest else None

        if status_in.status == RouteStatusEnum.FAILED:
            if current == RouteStatusEnum.DELIVERED:
                raise HTTPException(
                    status_code=409,
                    detail="Cannot mark delivered route as failed",
                )
            return await crud_route_status.create_route_status(
                db, route_id, status_in
            )

        allowed_next = ALLOWED_TRANSITIONS.get(current)
        if status_in.status != allowed_next:
            raise HTTPException(
                status_code=409,
                detail=f"Invalid status transition: "
                f"{current} → {status_in.status}",
            )

        new_status = await crud_route_status.create_route_status(
            db, route_id, status_in
        )
        await self._handle_status_transition_side_effects(
            db, route_id, status_in.status
        )
        return new_status

    async def _handle_status_transition_side_effects(
        self, db: AsyncSession, route_id: int, status: RouteStatusEnum
    ) -> None:
        route_update = None
        order_update = None

        if status == RouteStatusEnum.IN_TRANSIT:
            route = await route_service.get_route_or_404(db, route_id)
            now = datetime.now()
            new_eta = route_service.calculate_eta(route.order.distance, now)
            route_update = RouteUpdate(started_at=now, eta=new_eta)
            order_update = OrderUpdate(status=OrderStatus.IN_PROGRESS)
        elif status == RouteStatusEnum.DELIVERED:
            fuel_cost = await self._calculate_fuel_cost(db, route_id)
            route_update = RouteUpdate(
                completed_at=datetime.now(),
                fuel_cost=fuel_cost,
            )
            order_update = OrderUpdate(status=OrderStatus.COMPLETED)

        if route_update:
            updated_route = await route_service.update_route(
                db, route_id, route_update
            )
            if order_update:
                updated_order = await crud_order.update_order(
                    db, updated_route.order, order_update
                )
                if updated_order.status == OrderStatus.COMPLETED:
                    await self._sync_invoice(db, updated_order)

    async def _calculate_fuel_cost(
        self, db: AsyncSession, route_id: int
    ) -> float | None:
        route = await route_service.get_route_or_404(db, route_id)
        vehicle = None
        if route.vehicle_id:
            vehicle = await vehicle_service.get_vehicle_or_404(
                db, route.vehicle_id
            )
        elif route.driver_id:
            vehicles = await vehicle_service.get_driver_vehicles(
                db, route.driver_id
            )
            if vehicles:
                vehicle = vehicles[0]

        if not vehicle:
            return None

        return round(
            ((route.order.distance * vehicle.fuel_consumption) / 100)
            * vehicle.fuel_price,
            2,
        )

    async def _sync_invoice(self, db: AsyncSession, order) -> None:
        try:
            await invoice_service.add_order_to_invoice(db, order)
        except Exception as e:
            print(f"Failed to update invoice: {e}")


route_status_service = RouteStatusService()
