import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlmodel import SQLModel

from alembic import context
from app.core.config import settings
from app.models.delivery_photo import DeliveryPhoto
from app.models.invoice import Invoice
from app.models.notification import Notification
from app.models.order import Order
from app.models.route import Route
from app.models.route_status import RouteStatus
from app.models.shipment import Shipment
from app.models.user import User
from app.models.vehicle import Vehicle

_ = (
    User,
    Order,
    Route,
    RouteStatus,
    Shipment,
    Notification,
    Vehicle,
    DeliveryPhoto,
    Invoice,
)

config = context.config

config.set_main_option("sqlalchemy.url", str(settings.DATABASE_URL))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
