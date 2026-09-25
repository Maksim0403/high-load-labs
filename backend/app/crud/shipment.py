from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col

from app.models.shipment import Shipment
from app.schemas.shipment import ShipmentCreate, ShipmentUpdate


async def get_shipment_by_id(
    db: AsyncSession, shipment_id: int
) -> Optional[Shipment]:
    result = await db.execute(
        select(Shipment).where(col(Shipment.id) == shipment_id)
    )
    return result.scalars().first()


async def get_shipment_by_order_id(
    db: AsyncSession, order_id: int
) -> Optional[Shipment]:
    result = await db.execute(
        select(Shipment).where(col(Shipment.order_id) == order_id)
    )
    return result.scalars().first()


async def get_shipments(
    db: AsyncSession, order_id: Optional[int] = None
) -> Sequence[Shipment]:
    query = select(Shipment)
    if order_id is not None:
        query = query.where(col(Shipment.order_id) == order_id)
    result = await db.execute(query)
    return result.scalars().all()


async def create_shipment(
    db: AsyncSession, order_id: int, shipment_in: ShipmentCreate
) -> Shipment:
    db_shipment = Shipment(
        order_id=order_id,
        weight=shipment_in.weight,
        volume=shipment_in.volume,
        quantity=shipment_in.quantity,
        description=shipment_in.description,
    )
    db.add(db_shipment)
    await db.commit()
    await db.refresh(db_shipment)
    return db_shipment


async def update_shipment(
    db: AsyncSession, shipment: Shipment, shipment_in: ShipmentUpdate
) -> Shipment:
    update_data = shipment_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(shipment, field, value)
    db.add(shipment)
    await db.commit()
    await db.refresh(shipment)
    return shipment


async def delete_shipment(db: AsyncSession, shipment: Shipment) -> None:
    await db.delete(shipment)
    await db.commit()
