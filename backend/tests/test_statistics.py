from datetime import datetime

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import UserRole
from app.models.invoice import Invoice


@pytest.mark.asyncio
async def test_get_monthly_statistics_manager(
    client: AsyncClient, db_session: AsyncSession
):
    manager_payload = {
        "email": "manager_stats@example.com",
        "password": "password123",
        "full_name": "Stats Manager",
        "role": UserRole.MANAGER,
        "phone_number": "+380990001199",
    }
    await client.post("/api/v1/auth/register", json=manager_payload)
    await client.post(
        "/api/v1/auth/login",
        json={"email": "manager_stats@example.com", "password": "password123"},
    )

    invoice1 = Invoice(
        owner_id=1,
        billing_month=datetime(2024, 1, 15),
        total_shipment=2,
        total_weight=100.5,
        total_volume=50.0,
        total_distance=200.0,
    )
    invoice2 = Invoice(
        owner_id=1,
        billing_month=datetime(2024, 1, 20),
        total_shipment=1,
        total_weight=50.0,
        total_volume=20.0,
        total_distance=100.0,
    )
    invoice3 = Invoice(
        owner_id=1,
        billing_month=datetime(2024, 2, 10),
        total_shipment=5,
        total_weight=300.0,
        total_volume=150.0,
        total_distance=600.0,
    )
    db_session.add_all([invoice1, invoice2, invoice3])
    await db_session.commit()

    response = await client.get("/api/v1/dashboard/statistics/monthly")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    expected_months_count = 2
    assert len(data) == expected_months_count

    stats_feb = next(s for s in data if "2024-02" in s["month"])
    stats_jan = next(s for s in data if "2024-01" in s["month"])

    expected_feb_shipments = 5
    expected_feb_weight = 300.0
    expected_feb_invoices = 1
    assert stats_feb["total_shipments"] == expected_feb_shipments
    assert stats_feb["total_weight"] == expected_feb_weight
    assert stats_feb["invoice_count"] == expected_feb_invoices

    expected_jan_shipments = 3
    expected_jan_weight = 150.5
    expected_jan_distance = 300.0
    expected_jan_invoices = 2
    assert stats_jan["total_shipments"] == expected_jan_shipments
    assert stats_jan["total_weight"] == expected_jan_weight
    assert stats_jan["total_distance"] == expected_jan_distance
    assert stats_jan["invoice_count"] == expected_jan_invoices


@pytest.mark.asyncio
async def test_get_monthly_statistics_client_filtering(
    client: AsyncClient, db_session: AsyncSession
):
    client1_payload = {
        "email": "client1@example.com",
        "password": "password123",
        "full_name": "Client One",
        "role": UserRole.CLIENT,
        "phone_number": "+380990002211",
    }
    await client.post("/api/v1/auth/register", json=client1_payload)

    client2_payload = {
        "email": "client2@example.com",
        "password": "password123",
        "full_name": "Client Two",
        "role": UserRole.CLIENT,
        "phone_number": "+380990002222",
    }
    await client.post("/api/v1/auth/register", json=client2_payload)

    inv1 = Invoice(
        owner_id=1,
        billing_month=datetime(2024, 3, 1),
        total_shipment=10,
        total_weight=100,
        total_volume=10,
        total_distance=100,
    )
    inv2 = Invoice(
        owner_id=2,
        billing_month=datetime(2024, 3, 1),
        total_shipment=20,
        total_weight=200,
        total_volume=20,
        total_distance=200,
    )
    db_session.add_all([inv1, inv2])
    await db_session.commit()

    await client.post(
        "/api/v1/auth/login",
        json={"email": "client1@example.com", "password": "password123"},
    )
    response = await client.get("/api/v1/dashboard/statistics/monthly")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    expected_count = 1
    expected_shipments = 10
    expected_invoices = 1
    assert len(data) == expected_count
    assert data[0]["total_shipments"] == expected_shipments
    assert data[0]["invoice_count"] == expected_invoices
