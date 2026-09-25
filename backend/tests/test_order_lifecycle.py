from datetime import datetime, timedelta

import pytest
from fastapi import status
from httpx import AsyncClient

from app.enums import OrderStatus, RouteStatusEnum, UserRole


@pytest.mark.asyncio
async def test_manager_access_to_any_order(client: AsyncClient):
    client_reg = {
        "email": "client@example.com",
        "password": "password123",
        "full_name": "Client User",
        "role": UserRole.CLIENT,
        "phone_number": "+380990001144",
    }
    await client.post("/api/v1/auth/register", json=client_reg)
    await client.post(
        "/api/v1/auth/login",
        json={"email": "client@example.com", "password": "password123"},
    )

    order_resp = await client.post(
        "/api/v1/orders/",
        json={"title": "Client Order", "weight": 10.0, "distance": 100.0},
    )
    order_id = order_resp.json()["id"]

    await client.post("/api/v1/auth/logout")

    manager_reg = {
        "email": "manager@example.com",
        "password": "password123",
        "full_name": "Manager User",
        "role": UserRole.MANAGER,
        "phone_number": "+380990001155",
    }
    await client.post("/api/v1/auth/register", json=manager_reg)
    await client.post(
        "/api/v1/auth/login",
        json={"email": "manager@example.com", "password": "password123"},
    )

    get_resp = await client.get(f"/api/v1/dashboard/orders/{order_id}")
    assert get_resp.status_code == status.HTTP_200_OK
    assert get_resp.json()["id"] == order_id

    patch_resp = await client.patch(
        f"/api/v1/dashboard/orders/{order_id}",
        json={"title": "Updated by Manager"},
    )
    assert patch_resp.status_code == status.HTTP_200_OK
    assert patch_resp.json()["title"] == "Updated by Manager"


@pytest.mark.asyncio
async def test_cancel_order_in_progress(client: AsyncClient):
    manager_reg = {
        "email": "manager2@example.com",
        "password": "password123",
        "full_name": "Manager User 2",
        "role": UserRole.MANAGER,
        "phone_number": "+380990001156",
    }
    await client.post("/api/v1/auth/register", json=manager_reg)
    await client.post(
        "/api/v1/auth/login",
        json={"email": "manager2@example.com", "password": "password123"},
    )

    order_resp = await client.post(
        "/api/v1/orders/",
        json={"title": "Cancel Test", "weight": 20.0, "distance": 50.0},
    )
    assert order_resp.status_code == status.HTTP_201_CREATED
    order_id = order_resp.json()["id"]

    await client.patch(
        f"/api/v1/orders/{order_id}", json={"status": OrderStatus.IN_PROGRESS}
    )

    cancel_resp = await client.patch(
        f"/api/v1/orders/{order_id}", json={"status": OrderStatus.CANCELED}
    )
    assert cancel_resp.status_code == status.HTTP_200_OK
    assert cancel_resp.json()["status"] == OrderStatus.CANCELED


@pytest.mark.asyncio
async def test_route_sync_order_status(client: AsyncClient):
    manager_reg = {
        "email": "manager3@example.com",
        "password": "password123",
        "full_name": "Manager User 3",
        "role": UserRole.MANAGER,
        "phone_number": "+380990001157",
    }
    await client.post("/api/v1/auth/register", json=manager_reg)
    await client.post(
        "/api/v1/auth/login",
        json={"email": "manager3@example.com", "password": "password123"},
    )

    driver_reg = {
        "email": "driver2@example.com",
        "password": "password123",
        "full_name": "Driver User 2",
        "role": UserRole.DRIVER,
        "phone_number": "+380990001167",
    }
    driver_resp = await client.post("/api/v1/auth/register", json=driver_reg)
    driver_id = driver_resp.json()["id"]

    # Login as driver to create a vehicle
    await client.post("/api/v1/auth/logout")
    await client.post(
        "/api/v1/auth/login",
        json={"email": "driver2@example.com", "password": "password123"},
    )
    vehicle_payload = {
        "brand": "Ford",
        "model": "Transit",
        "license_plate": "AA1234BB",
        "max_weight": 1000.0,
        "max_volume": 10.0,
        "fuel_consumption": 10.0,
        "fuel_price": 50.0,
        "current_mileage": 0,
        "maintenance_interval": 10000,
    }
    veh_resp = await client.post(
        "/api/v1/dashboard/vehicles", json=vehicle_payload
    )
    vehicle_id = veh_resp.json()["id"]

    # Logout driver, login back as manager
    await client.post("/api/v1/auth/logout")
    await client.post(
        "/api/v1/auth/login",
        json={"email": "manager3@example.com", "password": "password123"},
    )

    order_resp = await client.post(
        "/api/v1/orders/",
        json={"title": "Sync Test", "weight": 30.0, "distance": 150.0},
    )
    assert order_resp.status_code == status.HTTP_201_CREATED
    order_id = order_resp.json()["id"]

    eta = (datetime.now() + timedelta(days=1)).isoformat()
    assign_resp = await client.post(
        f"/api/v1/dashboard/orders/{order_id}/assign",
        json={"driver_id": driver_id, "vehicle_id": vehicle_id, "eta": eta},
    )
    route_id = assign_resp.json()["id"]

    await client.post("/api/v1/auth/logout")

    await client.post(
        "/api/v1/auth/login",
        json={"email": "driver2@example.com", "password": "password123"},
    )

    await client.post(
        f"/api/v1/dashboard/routes/{route_id}/statuses",
        json={"status": RouteStatusEnum.ASSIGNED},
    )
    await client.post(
        f"/api/v1/dashboard/routes/{route_id}/statuses",
        json={"status": RouteStatusEnum.LOADED},
    )
    await client.post(
        f"/api/v1/dashboard/routes/{route_id}/statuses",
        json={"status": RouteStatusEnum.IN_TRANSIT},
    )

    order_check = await client.get(f"/api/v1/orders/{order_id}")
    assert order_check.json()["status"] == OrderStatus.IN_PROGRESS

    await client.post(
        f"/api/v1/dashboard/routes/{route_id}/statuses",
        json={"status": RouteStatusEnum.DELIVERED},
    )

    order_check2 = await client.get(f"/api/v1/orders/{order_id}")
    assert order_check2.json()["status"] == OrderStatus.COMPLETED
