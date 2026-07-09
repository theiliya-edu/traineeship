import asyncio
import datetime
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from redis.asyncio import Redis

from shared.cache import RedisCacheService
from spimex_api.api.routers import cache, trading_results
from spimex_api.config import settings
from spimex_api.logger import logger


async def _daily_cache_invalidator(redis: Redis) -> None:
    cache_service = RedisCacheService(redis)

    target_hour = 14
    target_minute = 11

    while True:
        # Получаем текущее время строго в UTC
        now = datetime.datetime.now(datetime.UTC)

        # Строим целевую точку на сегодня тоже в UTC
        target = now.replace(
            hour=target_hour,
            minute=target_minute,
            second=0,
            microsecond=0,
        )

        # Если 14:11 на сегодня уже прошло, переносим цель на завтра
        if now >= target:
            target += datetime.timedelta(days=1)

        # Считаем точное количество секунд для сна
        sleep_seconds = (target - now).total_seconds()
        logger.info("Следующий сброс кэша через %d секунд (в %s UTC)", sleep_seconds, target)

        await asyncio.sleep(sleep_seconds)

        # Сбрасываем кэш
        try:
            await cache_service.invalidate_by_prefix()
        except Exception:
            logger.exception("Ошибка при автоматической очистке кэша")
            # Небольшая пауза, чтобы при ошибке сеть не ушла в бесконечный цикл
            await asyncio.sleep(60)


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    logger.info(f"Старт приложения {application.title}...")

    redis = Redis.from_url(settings.redis.url, decode_responses=True)  # pyright: ignore[reportUnknownMemberType]
    application.state.redis = redis

    invalidator = asyncio.create_task(_daily_cache_invalidator(redis))

    yield

    invalidator.cancel()
    with suppress(asyncio.CancelledError):
        await invalidator

    await redis.close()
    logger.info("Завершение приложения...")


app = FastAPI(lifespan=lifespan)
app.include_router(trading_results.router, prefix="/v1")
app.include_router(cache.router, prefix="/v1")
