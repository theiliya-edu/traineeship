from typing import Annotated

from fastapi import APIRouter, Depends, Query

from spimex_api.api.dependencies import (
    get_pagination,
    get_service,
    get_trading_filters,
)
from spimex_api.api.schemas import (
    DynamicsFilters,
    PaginatedTradingResults,
    PaginationParams,
    TradingDateResponse,
    TradingResultFilters,
    TradingResultResponse,
)
from spimex_api.services import TradingResultService


router = APIRouter(tags=["trading-results"])


@router.get("/trading-results/dates", summary="Получить последние даты торгов")
async def get_last_trading_dates(
    limit: Annotated[int, Query(..., description="Количество торговых дней")],
    service: Annotated[TradingResultService, Depends(get_service)],
) -> list[TradingDateResponse]:
    return await service.get_last_trading_dates(limit)


@router.get("/trading-results/dynamics", summary="Получить динамику торгов за период")
async def get_dynamics(
    filters: Annotated[DynamicsFilters, Query()],
    service: Annotated[TradingResultService, Depends(get_service)],
) -> list[TradingResultResponse]:
    return await service.get_dynamics(filters)


@router.get("/trading-results", summary="Получить результаты торгов с фильтрацией и пагинацией")
async def get_trading_results(
    filters: Annotated[TradingResultFilters, Depends(get_trading_filters)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    service: Annotated[TradingResultService, Depends(get_service)],
) -> PaginatedTradingResults:
    return await service.get_trading_results(filters, pagination)
