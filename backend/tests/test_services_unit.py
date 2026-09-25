from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException, status

from app.enums import UserRole
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.services.user_service import UserService


@pytest.fixture
def user_service():
    return UserService()


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.mark.asyncio
async def test_unit_register_new_user_success(user_service, mock_db):
    user_in = UserCreate(
        email="new@example.com",
        password="password123",
        full_name="New User",
        role=UserRole.CLIENT,
        phone_number="+380000000000",
    )

    with patch(
        "app.crud.user.get_user_by_email", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = None

        with patch(
            "app.crud.user.create_user", new_callable=AsyncMock
        ) as mock_create:
            expected_user = User(
                id=1, email=user_in.email, full_name=user_in.full_name
            )
            mock_create.return_value = expected_user

            result = await user_service.register_new_user(
                mock_db, user_in=user_in
            )

            assert result == expected_user
            mock_get.assert_called_once_with(mock_db, email=user_in.email)
            mock_create.assert_called_once()


@pytest.mark.asyncio
async def test_unit_register_user_already_exists(user_service, mock_db):
    user_in = UserCreate(
        email="exists@example.com",
        password="password123",
        full_name="Existing User",
        role=UserRole.CLIENT,
        phone_number="+380000000001",
    )

    with patch(
        "app.crud.user.get_user_by_email", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = User(id=1, email=user_in.email)

        with pytest.raises(HTTPException) as exc:
            await user_service.register_new_user(mock_db, user_in=user_in)

        assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc.value.detail == "User already exists"


@pytest.mark.asyncio
async def test_unit_authenticate_success(user_service, mock_db):
    user_login = UserLogin(
        email="auth@example.com", password="correct_password"
    )
    hashed_password = "hashed_correct_password"
    db_user = User(
        id=1, email="auth@example.com", hashed_password=hashed_password
    )

    with patch(
        "app.crud.user.get_user_by_email", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = db_user

        with patch(
            "app.services.user_service.verify_password", return_value=True
        ):
            result = await user_service.authenticate(
                mock_db, user_in=user_login
            )

            assert result == db_user
            assert result.email == user_login.email
