from typing import AsyncGenerator

import jwt
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import SessionLocal
from app.enums import UserRole
from app.models.user import User
from app.services.user_service import user_service


async def get_db() -> AsyncGenerator:
    async with SessionLocal() as db:
        yield db


async def get_current_user(
    request: Request, db: AsyncSession = Depends(get_db)
) -> User:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        token_type: str = payload.get("type")

        if email is None or token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user = await user_service.get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


def require_roles(*roles: UserRole):
    async def dependency(current_user=Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="Access denied")
        return current_user

    return dependency
