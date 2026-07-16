from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from shared.cache import RedisCacheService
from shared.database.models import Base
from spimex_api.api.dependencies import get_redis, get_session
from spimex_api.main import app
from spimex_api.repository import TradingResultRepository
from spimex_api.services import TradingResultService


@pytest.fixture(scope="session")
def postgres_url():
    with PostgresContainer("postgres:17-alpine", driver="psycopg") as postgres:
        yield postgres.get_connection_url(driver="asyncpg")


@pytest.fixture(scope="session")
async def db_connection(postgres_url: str):
    engine = create_async_engine(postgres_url, echo=False)
    async with engine.connect() as connection:
        await connection.run_sync(Base.metadata.create_all)
        await connection.commit()
        yield connection

    await engine.dispose()


@pytest.fixture
async def db_session(db_connection: AsyncConnection):
    transaction = await db_connection.begin()
    session = AsyncSession(
        bind=db_connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )

    try:
        yield session
    finally:
        await session.close()
        await transaction.rollback()


@pytest.fixture
def override_get_session(db_session):
    async def _override():
        return db_session

    return _override


@pytest.fixture
def mock_redis():
    mock = AsyncMock(spec=Redis)
    mock.get = AsyncMock(return_value=None)
    mock.set = AsyncMock()
    mock.scan = AsyncMock(return_value=(0, []))
    mock.unlink = AsyncMock()
    return mock


@pytest.fixture
def dependency_overrides(override_get_session, mock_redis):
    app.dependency_overrides[get_session] = override_get_session

    async def _mock_get_redis():
        return mock_redis

    app.dependency_overrides[get_redis] = _mock_get_redis

    yield

    app.dependency_overrides.clear()


@pytest.fixture
async def client(dependency_overrides):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def repo(db_session):
    return TradingResultRepository(db_session)


@pytest.fixture
def mock_cache_service():
    return AsyncMock(spec=RedisCacheService)


@pytest.fixture
def service_with_mocks(repo, mock_cache_service):
    return TradingResultService(trading_repo=repo, cache=mock_cache_service)
