import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
)
from app.schemas.user import UserCreate, UserLogin, UserOut
from app.services.user_service import user_service

router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=201)
async def register(
    user_in: UserCreate, db: AsyncSession = Depends(deps.get_db)
):
    return await user_service.register_new_user(db, user_in=user_in)


@router.post("/login", response_model=UserOut)
async def login(
    response: Response,
    user_in: UserLogin,
    db: AsyncSession = Depends(deps.get_db),
):
    user = await user_service.authenticate(db, user_in=user_in)

    access_token = create_access_token(
        data={"sub": user.email, "role": user.role}
    )
    refresh_token = create_refresh_token(data={"sub": user.email})

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=settings.COOKIE_SECURE,
        path="/api/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        samesite="lax",
        secure=settings.COOKIE_SECURE,
        path="/api/v1/auth/refresh",
    )
    return user


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite="lax",
        secure=settings.COOKIE_SECURE,
        path="/api/",
    )
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        samesite="lax",
        secure=settings.COOKIE_SECURE,
        path="/api/v1/auth/refresh",
    )


@router.post("/refresh")
async def refresh_token(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(deps.get_db),
):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        user = await user_service.get_user_by_email(
            db, email=payload.get("sub")
        )
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        new_access_token = create_access_token(
            data={"sub": user.email, "role": user.role}
        )

        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            samesite="lax",
            secure=settings.COOKIE_SECURE,
            path="/api/",
        )
        return None
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
