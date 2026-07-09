import datetime
from typing import Any

from shared.cache import RedisCacheService
from spimex_api.api.schemas import (
    DynamicsFilters,
    PaginatedTradingResults,
    PaginationParams,
    TradingDateResponse,
    TradingResultFilters,
    TradingResultResponse,
)
from spimex_api.config import settings
from spimex_api.logger import logger
from spimex_api.repository import TradingResultRepository


class TradingResultService:
    def __init__(
        self,
        trading_repo: TradingResultRepository,
        cache: RedisCacheService,
        ttl: int = settings.redis.ttl,
    ) -> None:
        self.trading_repo = trading_repo
        self.cache = cache
        self.ttl = ttl

    async def try_get_cache(
        self,
        endpoint: str,
        **params: Any,  # type: ignore[explicit-any]
    ) -> tuple[str, Any | None]:  # type: ignore[explicit-any]
        key = self.cache.build_key(endpoint, **params)
        cached = await self.cache.get(key)

        if cached is not None:
            logger.info("Cache HIT for key=%s", key)
            return key, cached

        logger.info("Cache MISS for key=%s", key)
        return key, cached

    async def get_last_trading_dates(self, limit: int) -> list[TradingDateResponse]:
        key, cached = await self.try_get_cache("last_trading_dates", limit=limit)

        if cached is not None:
            return [TradingDateResponse(date=datetime.date.fromisoformat(d)) for d in cached]

        results = await self.trading_repo.get_last_trading_dates(limit)

        response = [TradingDateResponse(date=r) for r in results]
        await self.cache.set(key, [r.date.isoformat() for r in response], self.ttl)

        return response

    async def get_dynamics(self, filters: DynamicsFilters) -> list[TradingResultResponse]:
        key, cached = await self.try_get_cache("dynamics", **filters.model_dump(mode="json"))

        if cached is not None:
            return [TradingResultResponse.model_validate(item) for item in cached]

        results = await self.trading_repo.get_dynamics(
            oil_id=filters.oil_id,
            delivery_basis_id=filters.delivery_basis_id,
            delivery_type_id=filters.delivery_type_id,
            start_date=filters.start_date,
            end_date=filters.end_date,
        )

        response = [TradingResultResponse.model_validate(r) for r in results]
        await self.cache.set(key, [r.model_dump(mode="json") for r in response], self.ttl)

        return response

    async def get_trading_results(
        self,
        filters: TradingResultFilters,
        pagination: PaginationParams,
    ) -> PaginatedTradingResults:
        params = {
            **filters.model_dump(mode="json"),
            **pagination.model_dump(mode="json"),
        }
        key, cached = await self.try_get_cache("trading_results", **params)

        if cached is not None:
            return PaginatedTradingResults.model_validate(cached)

        results, total = await self.trading_repo.get_trading_results(
            oil_id=filters.oil_id,
            delivery_basis_id=filters.delivery_basis_id,
            delivery_type_id=filters.delivery_type_id,
            limit=pagination.limit,
            offset=pagination.offset,
        )

        items = [TradingResultResponse.model_validate(r) for r in results]
        response = PaginatedTradingResults(
            items=items,
            total=total,
            page=(pagination.offset // pagination.limit) + 1,
            limit=pagination.limit,
        )
        await self.cache.set(key, response.model_dump(mode="json"), self.ttl)

        return response
