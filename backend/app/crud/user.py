from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import get_password_hash
from app.enums import UserRole
from app.models.user import User
from app.schemas.user import UserCreate


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(
        select(User)
        .where(User.email == email)
        .options(selectinload(User.vehicle))
    )
    return result.scalars().first()


async def get_user_by_phone(db: AsyncSession, phone: str):
    result = await db.execute(
        select(User)
        .where(User.phone_number == phone)
        .options(selectinload(User.vehicle))
    )
    return result.scalars().first()


async def get_users_by_role(db: AsyncSession, role: UserRole):
    result = await db.execute(
        select(User)
        .where(User.role == role)
        .options(selectinload(User.vehicle))
    )
    return result.scalars().all()


async def get_user_by_id(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.vehicle))
    )
    return result.scalars().first()


async def create_user(db: AsyncSession, user_in: UserCreate):
    db_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role,
        full_name=user_in.full_name,
        phone_number=user_in.phone_number,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    await db.execute(
        select(User)
        .where(User.id == db_user.id)
        .options(selectinload(User.vehicle))
    )

    return db_user
