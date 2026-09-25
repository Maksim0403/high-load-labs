import pytest
from fastapi import status
from httpx import AsyncClient

from app.enums import UserRole


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    payload = {
        "email": "test@example.com",
        "password": "strongpassword123",
        "full_name": "Test User",
        "role": UserRole.CLIENT,
        "phone_number": "+380991112233",
    }
    response = await client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["full_name"] == payload["full_name"]
    assert data["role"] == UserRole.CLIENT
    assert "id" in data


@pytest.mark.asyncio
async def test_login_user(client: AsyncClient):
    payload = {
        "email": "login@example.com",
        "password": "testpassword",
        "full_name": "Login User",
        "role": UserRole.MANAGER,
        "phone_number": "+380994445566",
    }
    await client.post("/api/v1/auth/register", json=payload)

    login_data = {
        "email": "login@example.com",
        "password": "testpassword",
    }
    response = await client.post("/api/v1/auth/login", json=login_data)

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies

    data = response.json()
    assert data["email"] == login_data["email"]


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient):
    payload = {
        "email": "wrongpass@example.com",
        "password": "rightpassword",
        "full_name": "Wrong Pass User",
        "role": UserRole.CLIENT,
        "phone_number": "+380997778899",
    }
    await client.post("/api/v1/auth/register", json=payload)

    login_data = {
        "email": "wrongpass@example.com",
        "password": "wrongpassword",
    }
    response = await client.post("/api/v1/auth/login", json=login_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Incorrect email, phone or password"
