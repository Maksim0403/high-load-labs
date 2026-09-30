from datetime import UTC, datetime

import pytest
from redis.exceptions import RedisError

from app.enums import OrderStatus
from app.schemas.order import OrderOut
from app.services.order_cache import OrderCache

ORDER_ID = 42
OWNER_ID = 7
TTL_SECONDS = 45


class FakeRedis:
    def __init__(self):
        self.values = {}
        self.expirations = {}
        self.fail = False

    async def get(self, key: str):
        if self.fail:
            raise RedisError("Redis unavailable")
        return self.values.get(key)

    async def set(self, key: str, value: str, ex: int):
        if self.fail:
            raise RedisError("Redis unavailable")
        self.values[key] = value
        self.expirations[key] = ex

    async def delete(self, key: str):
        if self.fail:
            raise RedisError("Redis unavailable")
        return int(self.values.pop(key, None) is not None)


def sample_order() -> OrderOut:
    return OrderOut(
        id=42,
        title="Cached order",
        description=None,
        origin_address=None,
        destination_address=None,
        weight=10,
        total_amount=0,
        distance=50,
        is_template=False,
        owner_id=7,
        status=OrderStatus.PENDING,
        created_at=datetime.now(UTC),
        received_at=None,
    )


@pytest.mark.asyncio
async def test_order_cache_miss_hit_ttl_and_invalidation():
    redis = FakeRedis()
    cache = OrderCache(redis, enabled=True, ttl_seconds=TTL_SECONDS)

    order, status = await cache.get(ORDER_ID)
    assert order is None
    assert status == "MISS"
    assert OrderCache.key(ORDER_ID) == "logiflow:order:v1:42"

    assert await cache.set(sample_order()) == "MISS"
    assert redis.expirations[OrderCache.key(ORDER_ID)] == TTL_SECONDS

    cached, status = await cache.get(ORDER_ID)
    assert status == "HIT"
    assert cached is not None
    assert cached.id == ORDER_ID
    assert cached.title == "Cached order"
    assert cached.owner_id == OWNER_ID

    assert await cache.invalidate(ORDER_ID)
    assert await cache.get(ORDER_ID) == (None, "MISS")


@pytest.mark.asyncio
async def test_order_cache_bypasses_redis_errors():
    redis = FakeRedis()
    cache = OrderCache(redis, enabled=True, ttl_seconds=TTL_SECONDS)
    redis.fail = True

    order, status = await cache.get(ORDER_ID)

    assert order is None
    assert status == "BYPASS"
    assert await cache.set(sample_order()) == "BYPASS"
    assert not await cache.invalidate(ORDER_ID)


@pytest.mark.asyncio
async def test_disabled_order_cache_does_not_access_redis():
    redis = FakeRedis()
    redis.fail = True
    cache = OrderCache(redis, enabled=False, ttl_seconds=TTL_SECONDS)

    assert await cache.get(ORDER_ID) == (None, "BYPASS")
    assert await cache.set(sample_order()) == "BYPASS"
    assert not await cache.invalidate(ORDER_ID)
