import os
from typing import AsyncGenerator

import asyncpg
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel

from app.api.deps import get_db
from app.core.config import settings
from app.main import app
from app.models.order import Order  # noqa: F401
from app.models.user import User  # noqa: F401

TEST_DB_NAME = os.getenv("DB_NAME", "logiflow_test")
TEST_DATABASE_URL = settings.DATABASE_URL.replace(
    f"/{settings.DB_NAME}", f"/{TEST_DB_NAME}"
)


async def create_test_db():
    conn_url = settings.DATABASE_URL.replace(
        f"/{settings.DB_NAME}", "/postgres"
    )
    pure_url = conn_url.replace("postgresql+asyncpg://", "")
    user_pass, host_port_db = pure_url.split("@")
    user, password = user_pass.split(":")
    host_port, _ = host_port_db.split("/")
    host, port = host_port.split(":")

    conn = await asyncpg.connect(
        user=user, password=password, host=host, port=port, database="postgres"
    )
    try:
        exists = await conn.fetchval(
            f"SELECT 1 FROM pg_database WHERE datname = '{TEST_DB_NAME}'"
        )
        if not exists:
            await conn.execute(f"CREATE DATABASE {TEST_DB_NAME}")
    finally:
        await conn.close()


engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)

TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
)


@pytest.fixture(scope="function", autouse=True)
async def initialize_tests():
    await create_test_db()
    yield


@pytest.fixture(autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
    yield


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture
async def client(
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncClient, None]:

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
