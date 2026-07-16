import datetime
from unittest.mock import AsyncMock

import pytest

from shared.cache import RedisCacheService
from spimex_api.api.schemas import DynamicsFilters, PaginationParams, TradingResultFilters
from spimex_api.repository import TradingResultRepository
from spimex_api.services import TradingResultService


@pytest.fixture
def mock_repo():
    return AsyncMock(spec=TradingResultRepository)


@pytest.fixture
def mock_cache():
    cache = AsyncMock(spec=RedisCacheService)
    cache.build_key.return_value = "test-key"
    cache.get.return_value = None
    return cache


@pytest.fixture
def service(mock_repo, mock_cache):
    return TradingResultService(trading_repo=mock_repo, cache=mock_cache)


@pytest.fixture
def result_data():
    return {
        "id": 1,
        "exchange_product_id": "A100BCC00",
        "oil_id": "A100",
        "delivery_basis_id": "BCC",
        "delivery_type_id": "0",
        "exchange_product_name": "Test",
        "delivery_basis_name": "Basis",
        "volume": 100,
        "total": 10000,
        "count": 10,
        "date": "2024-01-15",
    }


async def test_last_dates_cache_hit_skips_repository(service, mock_repo, mock_cache):
    mock_cache.get.return_value = ["2024-01-03", "2024-01-02"]

    result = await service.get_last_trading_dates(limit=2)

    assert [item.date for item in result] == [datetime.date(2024, 1, 3), datetime.date(2024, 1, 2)]
    mock_repo.get_last_trading_dates.assert_not_awaited()


async def test_last_dates_cache_miss_queries_repository_and_caches(service, mock_repo, mock_cache):
    mock_repo.get_last_trading_dates.return_value = [datetime.date(2024, 1, 3)]

    result = await service.get_last_trading_dates(limit=1)

    assert result[0].date == datetime.date(2024, 1, 3)
    mock_repo.get_last_trading_dates.assert_awaited_once_with(1)
    mock_cache.set.assert_awaited_once_with("test-key", ["2024-01-03"], service.ttl)


async def test_dynamics_cache_hit_deserializes_results(service, mock_repo, mock_cache, result_data):
    mock_cache.get.return_value = [result_data]
    filters = DynamicsFilters(oil_id="A100", delivery_basis_id="BCC", delivery_type_id="0")

    result = await service.get_dynamics(filters)

    assert result[0].oil_id == "A100"
    mock_repo.get_dynamics.assert_not_awaited()


async def test_dynamics_cache_miss_queries_repository_and_caches(service, mock_repo, mock_cache):
    filters = DynamicsFilters(
        oil_id="A100",
        delivery_basis_id="BCC",
        delivery_type_id="0",
        start_date=datetime.date(2024, 1, 1),
        end_date=datetime.date(2024, 1, 31),
    )
    mock_repo.get_dynamics.return_value = []

    result = await service.get_dynamics(filters)

    assert result == []
    mock_repo.get_dynamics.assert_awaited_once_with(
        oil_id="A100",
        delivery_basis_id="BCC",
        delivery_type_id="0",
        start_date=datetime.date(2024, 1, 1),
        end_date=datetime.date(2024, 1, 31),
    )
    mock_cache.set.assert_awaited_once_with("test-key", [], service.ttl)


async def test_trading_results_cache_hit_deserializes_page(service, mock_repo, mock_cache, result_data):
    mock_cache.get.return_value = {"items": [result_data], "total": 1, "page": 1, "limit": 10}
    filters = TradingResultFilters()
    pagination = PaginationParams(limit=10, offset=0)

    result = await service.get_trading_results(filters, pagination)

    assert result.total == 1
    assert result.items[0].oil_id == "A100"
    mock_repo.get_trading_results.assert_not_awaited()


async def test_trading_results_cache_miss_builds_and_caches_page(service, mock_repo, mock_cache):
    mock_repo.get_trading_results.return_value = ([], 0)
    filters = TradingResultFilters(oil_id="A100")
    pagination = PaginationParams(limit=5, offset=15)

    result = await service.get_trading_results(filters, pagination)

    assert result.page == 4
    assert result.total == 0
    mock_repo.get_trading_results.assert_awaited_once_with(
        oil_id="A100",
        delivery_basis_id=None,
        delivery_type_id=None,
        limit=5,
        offset=15,
    )
    mock_cache.set.assert_awaited_once_with("test-key", result.model_dump(mode="json"), service.ttl)
