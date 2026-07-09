import hashlib
import json
from typing import Any

from redis.asyncio import Redis


class RedisCacheService:
    CACHE_PREFIX: str = "spimex-api"

    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def get(self, key: str) -> Any | None:  # type: ignore[explicit-any]
        data = await self.redis.get(key)
        return json.loads(data) if data is not None else None

    async def set(self, key: str, value: Any, ttl: int) -> None:  # type: ignore[explicit-any]
        await self.redis.set(key, json.dumps(value, default=str), ex=ttl)

    def build_key(self, endpoint: str, **params: dict[str, Any]) -> str:  # type: ignore[explicit-any]
        canonical = json.dumps(params, sort_keys=True, default=str)
        return f"{self.CACHE_PREFIX}:{endpoint}:{hashlib.md5(canonical.encode()).hexdigest()}"

    async def invalidate_by_prefix(self) -> None:
        cursor = 0
        while True:
            cursor, keys = await self.redis.scan(cursor, match=f"{self.CACHE_PREFIX}*", count=100)
            if keys:
                await self.redis.unlink(*keys)
            if cursor == 0:
                break
