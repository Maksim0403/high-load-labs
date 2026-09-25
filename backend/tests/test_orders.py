import pytest
from fastapi import status
from httpx import AsyncClient

from app.enums import OrderStatus, UserRole


@pytest.mark.asyncio
async def test_create_order(client: AsyncClient):
    user_payload = {
        "email": "order_owner@example.com",
        "password": "password123",
        "full_name": "Order Owner",
        "role": UserRole.CLIENT,
        "phone_number": "+380990001122",
    }
    await client.post("/api/v1/auth/register", json=user_payload)

    login_data = {
        "email": "order_owner@example.com",
        "password": "password123",
    }
    await client.post("/api/v1/auth/login", json=login_data)

    order_payload = {
        "title": "Доставка будматеріалів",
        "description": "Привезти 10 мішків цементу",
        "weight": 500.5,
        "distance": 100.0,
    }

    response = await client.post("/api/v1/orders/", json=order_payload)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == order_payload["title"]
    assert data["description"] == order_payload["description"]
    assert data["weight"] == order_payload["weight"]
    assert data["status"] == OrderStatus.PENDING
    assert "id" in data
    assert "owner_id" in data


@pytest.mark.asyncio
async def test_create_order_template(client: AsyncClient):
    user_payload = {
        "email": "order_owner@example.com",
        "password": "password123",
        "full_name": "Order Owner",
        "role": UserRole.CLIENT,
        "phone_number": "+380990001122",
    }
    await client.post("/api/v1/auth/register", json=user_payload)

    login_data = {
        "email": "order_owner@example.com",
        "password": "password123",
    }
    await client.post("/api/v1/auth/login", json=login_data)

    order_payload = {
        "title": "Шаблон замовлення",
        "description": "Це шаблон для регулярної доставки",
        "weight": 100.0,
        "distance": 50.0,
        "is_template": True,
    }

    response = await client.post("/api/v1/orders/", json=order_payload)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == order_payload["title"]
    assert data["is_template"] is True


@pytest.mark.asyncio
async def test_get_order_templates(client: AsyncClient):
    user_payload = {
        "email": "order_owner@example.com",
        "password": "password123",
        "full_name": "Order Owner",
        "role": UserRole.CLIENT,
        "phone_number": "+380990001122",
    }
    await client.post("/api/v1/auth/register", json=user_payload)

    login_data = {
        "email": "order_owner@example.com",
        "password": "password123",
    }
    await client.post("/api/v1/auth/login", json=login_data)

    response = await client.get("/api/v1/orders/?is_template=true")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    for order in data:
        assert order["is_template"] is True


@pytest.mark.asyncio
async def test_create_order_unauthorized(client: AsyncClient):
    order_payload = {
        "title": "Спроба без логіну",
        "weight": 10.0,
        "distance": 10.0,
    }
    response = await client.post("/api/v1/orders/", json=order_payload)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_confirm_order_receipt(client: AsyncClient):
    user_payload = {
        "email": "confirm_test@example.com",
        "password": "password123",
        "full_name": "Confirm Tester",
        "role": UserRole.CLIENT,
        "phone_number": "+380990001133",
    }
    await client.post("/api/v1/auth/register", json=user_payload)
    login_data = {
        "email": "confirm_test@example.com",
        "password": "password123",
    }
    await client.post("/api/v1/auth/login", json=login_data)

    order_payload = {
        "title": "Test Confirmation",
        "weight": 50.0,
        "distance": 20.0,
    }
    create_response = await client.post("/api/v1/orders/", json=order_payload)
    order_id = create_response.json()["id"]

    fail_confirm = await client.post(f"/api/v1/orders/{order_id}/confirm")
    assert fail_confirm.status_code == status.HTTP_409_CONFLICT

    await client.patch(
        f"/api/v1/orders/{order_id}", json={"status": OrderStatus.IN_PROGRESS}
    )

    confirm_response = await client.post(f"/api/v1/orders/{order_id}/confirm")
    assert confirm_response.status_code == status.HTTP_200_OK
    data = confirm_response.json()
    assert data["status"] == OrderStatus.COMPLETED
    assert data["received_at"] is not None

    reconfirm_response = await client.post(
        f"/api/v1/orders/{order_id}/confirm"
    )
    assert reconfirm_response.status_code == status.HTTP_409_CONFLICT
