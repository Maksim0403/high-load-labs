from datetime import datetime

import pytest

# ruff: noqa: PLR2004
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import OrderStatus, UserRole
from app.models.order import Order


@pytest.mark.asyncio
async def test_get_daily_statistics_for_month(
    client: AsyncClient, db_session: AsyncSession
):
    manager_payload = {
        "email": "manager_daily@example.com",
        "password": "password123",
        "full_name": "Daily Manager",
        "role": UserRole.MANAGER,
        "phone_number": "+380990001188",
    }
    await client.post("/api/v1/auth/register", json=manager_payload)
    await client.post(
        "/api/v1/auth/login",
        json={"email": "manager_daily@example.com", "password": "password123"},
    )

    order1 = Order(
        title="Order 1",
        weight=10.0,
        distance=10.0,
        total_amount=100.0,
        status=OrderStatus.COMPLETED,
        received_at=datetime(2026, 5, 10, 10, 0),
        owner_id=1,
    )
    order2 = Order(
        title="Order 2",
        weight=20.0,
        distance=20.0,
        total_amount=200.0,
        status=OrderStatus.COMPLETED,
        received_at=datetime(2026, 5, 10, 15, 0),
        owner_id=1,
    )
    order3 = Order(
        title="Order 3",
        weight=30.0,
        distance=30.0,
        total_amount=300.0,
        status=OrderStatus.COMPLETED,
        received_at=datetime(2026, 5, 11, 10, 0),
        owner_id=1,
    )
    db_session.add_all([order1, order2, order3])
    await db_session.commit()

    response = await client.get(
        "/api/v1/dashboard/statistics/monthly?month=2026-05"
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert len(data) == 2

    data.sort(key=lambda x: x["month"])

    assert "2026-05-10" in data[0]["month"]
    assert data[0]["total_shipments"] == 2
    assert data[0]["total_weight"] == 30.0
    assert data[0]["total_amount"] == 300.0

    assert "2026-05-11" in data[1]["month"]
    assert data[1]["total_shipments"] == 1
    assert data[1]["total_weight"] == 30.0
    assert data[1]["total_amount"] == 300.0
