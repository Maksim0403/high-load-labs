from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password
from app.crud import user as crud_user
from app.schemas.user import UserCreate, UserLogin


class UserService:
    async def register_new_user(self, db: AsyncSession, user_in: UserCreate):
        user = await crud_user.get_user_by_email(db, email=user_in.email)
        if user:
            raise HTTPException(status_code=400, detail="User already exists")
        return await crud_user.create_user(db, user_in)

    async def authenticate(self, db: AsyncSession, user_in: UserLogin):
        user = None
        if user_in.email:
            user = await crud_user.get_user_by_email(db, email=user_in.email)
        elif user_in.phone_number:
            user = await crud_user.get_user_by_phone(
                db, phone=user_in.phone_number
            )

        if not user or not verify_password(
            user_in.password, user.hashed_password
        ):
            raise HTTPException(
                status_code=400, detail="Incorrect email, phone or password"
            )
        return user

    async def get_user_by_email(self, db: AsyncSession, email: str):
        return await crud_user.get_user_by_email(db, email=email)

    async def get_user_by_id(self, db: AsyncSession, user_id: int):
        return await crud_user.get_user_by_id(db, user_id=user_id)

    async def get_users_by_role(self, db: AsyncSession, role: str):
        return await crud_user.get_users_by_role(db, role=role)


user_service = UserService()
