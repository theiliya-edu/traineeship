import asyncio
from typing import override

from sqlalchemy import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from tqdm.asyncio import tqdm

from spimex_parser.domain.dto import SpimexTradingResultDTO
from spimex_parser.infrastructure.database.models import SpimexTradingResult
from spimex_parser.logger import logger
from spimex_parser.pipeline.workers.base import BaseWorkerPool


class SaveWorkerPool(BaseWorkerPool[list[SpimexTradingResultDTO]]):
    def __init__(
        self,
        db_batches_queue: asyncio.Queue[list[SpimexTradingResultDTO] | None],
        session_factory: async_sessionmaker[AsyncSession],
        pbar: tqdm,  # type: ignore[implicit-any-type-argument]
        *,
        concurrency: int = 1,
    ) -> None:
        super().__init__(db_batches_queue, pbar, concurrency)

        self.session_factory = session_factory

    @override
    async def _process_item(self, item: list[SpimexTradingResultDTO]) -> None:
        try:
            async with self.session_factory() as session:
                await session.execute(insert(SpimexTradingResult).values([row.model_dump() for row in item]))
                await session.commit()
        except SQLAlchemyError:
            logger.exception("Ошибка сохранения в БД")
