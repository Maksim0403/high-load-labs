from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.user import User
from app.schemas.vehicle import VehicleCreate, VehicleOut, VehicleUpdate
from app.services.vehicle_service import vehicle_service

router = APIRouter()


@router.get("/", response_model=list[VehicleOut])
async def get_my_vehicles(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get all vehicles for the current driver.
    """
    return await vehicle_service.get_driver_vehicles(db, current_user.id)


@router.post(
    "/", response_model=VehicleOut, status_code=status.HTTP_201_CREATED
)
async def add_vehicle(
    vehicle_in: VehicleCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Add a new vehicle for the current driver.
    """
    return await vehicle_service.add_vehicle(db, vehicle_in, current_user)


@router.get("/{vehicle_id}", response_model=VehicleOut)
async def get_vehicle(
    vehicle_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get vehicle by ID.
    """
    vehicle = await vehicle_service.get_vehicle_or_404(db, vehicle_id)
    vehicle_service._check_ownership(vehicle, current_user)
    return vehicle


@router.patch("/{vehicle_id}", response_model=VehicleOut)
async def update_vehicle(
    vehicle_id: int,
    vehicle_in: VehicleUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Update vehicle details.
    """
    return await vehicle_service.update_vehicle(
        db, vehicle_id, vehicle_in, current_user
    )


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vehicle(
    vehicle_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Delete a vehicle.
    """
    await vehicle_service.remove_vehicle(db, vehicle_id, current_user)
