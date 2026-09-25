from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleUpdate


async def get_vehicle_by_id(
    db: AsyncSession, vehicle_id: int
) -> Vehicle | None:
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
    return result.scalars().first()


async def get_vehicle_by_plate(db: AsyncSession, plate: str) -> Vehicle | None:
    result = await db.execute(
        select(Vehicle).where(Vehicle.license_plate == plate)
    )
    return result.scalars().first()


async def get_vehicles_by_driver(
    db: AsyncSession, driver_id: int
) -> list[Vehicle]:
    result = await db.execute(
        select(Vehicle).where(Vehicle.driver_id == driver_id)
    )
    return result.scalars().all()


async def create_vehicle(
    db: AsyncSession, vehicle_in: VehicleCreate, driver_id: int
) -> Vehicle:
    db_vehicle = Vehicle(**vehicle_in.model_dump(), driver_id=driver_id)
    db.add(db_vehicle)
    await db.commit()
    await db.refresh(db_vehicle)
    return db_vehicle


async def update_vehicle(
    db: AsyncSession, vehicle: Vehicle, data: VehicleUpdate
) -> Vehicle:
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(vehicle, field, value)
    db.add(vehicle)
    await db.commit()
    await db.refresh(vehicle)
    return vehicle


async def delete_vehicle(db: AsyncSession, vehicle: Vehicle) -> None:
    await db.delete(vehicle)
    await db.commit()
