from typing import Sequence

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import shipment as crud_shipment
from app.models.shipment import Shipment
from app.schemas.shipment import ShipmentCreate, ShipmentUpdate


class ShipmentService:
    async def get_shipment_or_404(
        self, db: AsyncSession, shipment_id: int
    ) -> Shipment:
        shipment = await crud_shipment.get_shipment_by_id(db, shipment_id)
        if not shipment:
            raise HTTPException(status_code=404, detail="Shipment not found")
        return shipment

    async def get_shipments_by_order(
        self, db: AsyncSession, order_id: int
    ) -> Sequence[Shipment]:
        return await crud_shipment.get_shipments(db, order_id=order_id)

    async def create_shipment(
        self, db: AsyncSession, order_id: int, shipment_in: ShipmentCreate
    ) -> Shipment:
        existing = await crud_shipment.get_shipment_by_order_id(db, order_id)
        if existing:
            raise HTTPException(
                status_code=409,
                detail="Shipment already exists for this order",
            )
        return await crud_shipment.create_shipment(db, order_id, shipment_in)

    async def update_shipment(
        self, db: AsyncSession, shipment_id: int, shipment_in: ShipmentUpdate
    ) -> Shipment:
        shipment = await self.get_shipment_or_404(db, shipment_id)
        return await crud_shipment.update_shipment(db, shipment, shipment_in)

    async def delete_shipment(
        self, db: AsyncSession, shipment_id: int
    ) -> None:
        shipment = await self.get_shipment_or_404(db, shipment_id)
        await crud_shipment.delete_shipment(db, shipment)


shipment_service = ShipmentService()
