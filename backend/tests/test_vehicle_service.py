from unittest.mock import AsyncMock, patch

import pytest

from app.models.user import User
from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleUpdate
from app.services.vehicle_service import vehicle_service


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def current_user():
    return User(id=1, email="driver@example.com")


@pytest.mark.asyncio
async def test_update_vehicle_mileage_triggers_notification(
    mock_db, current_user
):
    vehicle = Vehicle(
        id=1,
        driver_id=current_user.id,
        brand="Ford",
        model="Transit",
        license_plate="AB1234CD",
        max_weight=1000,
        max_volume=10,
        fuel_consumption=10,
        fuel_price=50.0,
        current_mileage=9900,
        maintenance_interval=10000,
    )

    update_data = VehicleUpdate(current_mileage=10050)

    updated_vehicle = Vehicle(
        id=1,
        driver_id=current_user.id,
        brand="Ford",
        model="Transit",
        license_plate="AB1234CD",
        max_weight=1000,
        max_volume=10,
        fuel_consumption=10,
        fuel_price=50.0,
        current_mileage=10050,
        maintenance_interval=10000,
    )

    with patch(
        "app.services.vehicle_service.crud_vehicle.get_vehicle_by_id",
        new_callable=AsyncMock,
    ) as mock_get:
        mock_get.return_value = vehicle

        with patch(
            "app.services.vehicle_service.crud_vehicle.update_vehicle",
            new_callable=AsyncMock,
        ) as mock_update:
            mock_update.return_value = updated_vehicle

            with patch(
                "app.services.vehicle_service.notification_service.create_notification",
                new_callable=AsyncMock,
            ) as mock_notify:
                result = await vehicle_service.update_vehicle(
                    mock_db,
                    vehicle_id=1,
                    data=update_data,
                    current_user=current_user,
                )

                assert result.current_mileage == update_data.current_mileage
                mock_notify.assert_called_once()
                args, kwargs = mock_notify.call_args
                assert kwargs["user_id"] == current_user.id
                assert "requires maintenance" in kwargs["message"]


@pytest.mark.asyncio
async def test_update_vehicle_mileage_no_notification(mock_db, current_user):
    vehicle = Vehicle(
        id=1,
        driver_id=current_user.id,
        brand="Ford",
        model="Transit",
        license_plate="AB1234CD",
        max_weight=1000,
        max_volume=10,
        fuel_consumption=10,
        fuel_price=50.0,
        current_mileage=9900,
        maintenance_interval=10000,
    )

    update_data = VehicleUpdate(current_mileage=9950)

    updated_vehicle = Vehicle(
        id=1,
        driver_id=current_user.id,
        brand="Ford",
        model="Transit",
        license_plate="AB1234CD",
        max_weight=1000,
        max_volume=10,
        fuel_consumption=10,
        fuel_price=50.0,
        current_mileage=9950,
        maintenance_interval=10000,
    )

    with patch(
        "app.services.vehicle_service.crud_vehicle.get_vehicle_by_id",
        new_callable=AsyncMock,
    ) as mock_get:
        mock_get.return_value = vehicle

        with patch(
            "app.services.vehicle_service.crud_vehicle.update_vehicle",
            new_callable=AsyncMock,
        ) as mock_update:
            mock_update.return_value = updated_vehicle

            with patch(
                "app.services.vehicle_service.notification_service.create_notification",
                new_callable=AsyncMock,
            ) as mock_notify:
                await vehicle_service.update_vehicle(
                    mock_db,
                    vehicle_id=1,
                    data=update_data,
                    current_user=current_user,
                )

                mock_notify.assert_not_called()
