import datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from shared.cache import RedisCacheService
from spimex_api.api.dependencies import get_redis


router = APIRouter(tags=["cache"])


@router.post("/trading-results/cache/invalidate", summary="Инвалидировать весь кэш")
async def invalidate_cache(redis: Annotated[Redis, Depends(get_redis)]) -> dict[str, str]:
    cache = RedisCacheService(redis)
    await cache.invalidate_by_prefix()
    return {"status": "ok", "invalidated_at": datetime.datetime.now().isoformat()}
