from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Query, Request
from pydantic.json_schema import SkipJsonSchema
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from shared.cache import RedisCacheService
from shared.database.helper import SessionFactory
from spimex_api.api.schemas import PaginationParams, TradingResultFilters
from spimex_api.repository import TradingResultRepository
from spimex_api.services import TradingResultService


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionFactory() as session:
        yield session


def get_repo(session: Annotated[AsyncSession, Depends(get_session)]) -> TradingResultRepository:
    return TradingResultRepository(session)


async def get_redis(request: Request) -> Redis:  # type: ignore[explicit-any]
    return request.app.state.redis


def get_cache_service(redis: Annotated[Redis, Depends(get_redis)]) -> RedisCacheService:
    return RedisCacheService(redis=redis)


def get_service(
    repo: Annotated[TradingResultRepository, Depends(get_repo)],
    cache: Annotated[RedisCacheService, Depends(get_cache_service)],
) -> TradingResultService:
    return TradingResultService(trading_repo=repo, cache=cache)


def get_pagination(
    limit: Annotated[int, Query(ge=1, le=100, description="Количество элементов на страницу")] = 10,
    offset: Annotated[
        int,
        Query(
            ge=0,
            description="Смещение относительно начала списка (пропуск N элементов)",
        ),
    ] = 0,
) -> PaginationParams:
    return PaginationParams(limit=limit, offset=offset)


def get_trading_filters(
    oil_id: Annotated[str | SkipJsonSchema[None], Query(description="Код нефти или нефтепродукта")] = None,
    delivery_basis_id: Annotated[str | SkipJsonSchema[None], Query(description="Код базиса поставки")] = None,
    delivery_type_id: Annotated[str | SkipJsonSchema[None], Query(description="Код типа поставки")] = None,
) -> TradingResultFilters:
    return TradingResultFilters(
        oil_id=oil_id,
        delivery_basis_id=delivery_basis_id,
        delivery_type_id=delivery_type_id,
    )
