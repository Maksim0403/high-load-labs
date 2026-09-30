import logging

from pydantic import ValidationError
from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.config import settings
from app.schemas.order import OrderOut

logger = logging.getLogger(__name__)


class OrderCache:
    def __init__(
        self,
        client: Redis,
        enabled: bool,
        ttl_seconds: int,
    ) -> None:
        self.client = client
        self.enabled = enabled
        self.ttl_seconds = ttl_seconds

    @staticmethod
    def key(order_id: int) -> str:
        return f"logiflow:order:v1:{order_id}"

    async def get(self, order_id: int) -> tuple[OrderOut | None, str]:
        if not self.enabled:
            return None, "BYPASS"

        key = self.key(order_id)
        try:
            cached = await self.client.get(key)
        except RedisError as exc:
            logger.warning("Order cache read failed: %s", exc)
            return None, "BYPASS"

        if cached is None:
            return None, "MISS"

        try:
            return OrderOut.model_validate_json(cached), "HIT"
        except ValidationError:
            logger.warning("Discarding invalid order cache entry: %s", key)
            try:
                await self.client.delete(key)
            except RedisError as exc:
                logger.warning("Order cache cleanup failed: %s", exc)
                return None, "BYPASS"
            return None, "MISS"

    async def set(self, order: OrderOut) -> str:
        if not self.enabled:
            return "BYPASS"

        try:
            await self.client.set(
                self.key(order.id),
                order.model_dump_json(),
                ex=self.ttl_seconds,
            )
        except RedisError as exc:
            logger.warning("Order cache write failed: %s", exc)
            return "BYPASS"
        return "MISS"

    async def invalidate(self, order_id: int) -> bool:
        if not self.enabled:
            return False

        key = self.key(order_id)
        try:
            await self.client.delete(key)
        except RedisError as exc:
            logger.warning(
                "Order cache invalidation failed for %s: %s", key, exc
            )
            return False

        logger.info("Order cache invalidated: %s", key)
        return True

    async def close(self) -> None:
        await self.client.aclose()


redis_client = Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=0.25,
    socket_timeout=0.25,
)
order_cache = OrderCache(
    client=redis_client,
    enabled=settings.ORDER_CACHE_ENABLED,
    ttl_seconds=settings.ORDER_CACHE_TTL_SECONDS,
)
