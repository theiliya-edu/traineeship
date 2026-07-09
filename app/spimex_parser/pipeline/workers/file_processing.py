import asyncio
from concurrent.futures import ProcessPoolExecutor
from typing import override

from tqdm.asyncio import tqdm

from spimex_parser.domain.dto import SpimexTradingResultDTO
from spimex_parser.logger import logger
from spimex_parser.pipeline.context import DownloadedFile
from spimex_parser.pipeline.workers.base import BaseWorkerPool
from spimex_parser.services.file_processing import process_file


class ProcessFileWorkerPool(BaseWorkerPool[DownloadedFile]):
    def __init__(
        self,
        files_queue: asyncio.Queue[DownloadedFile | None],
        db_batches_queue: asyncio.Queue[list[SpimexTradingResultDTO] | None],
        pbar: tqdm,  # type: ignore[implicit-any-type-argument]
        *,
        concurrency: int = 1,
    ) -> None:
        super().__init__(files_queue, pbar, concurrency)

        self.db_batches_queue = db_batches_queue
        self.executor = ProcessPoolExecutor(max_workers=concurrency)

    @override
    async def _process_item(self, item: DownloadedFile) -> None:
        try:
            (
                valid_rows,
                _invalid_rows,
            ) = await asyncio.get_running_loop().run_in_executor(
                self.executor,
                process_file,
                item.content,
                item.name,
            )
        except Exception:
            logger.exception("Ошибка обработки файла: %s", item.name)
            return

        await self.db_batches_queue.put(valid_rows)

    @override
    async def _on_stop(self) -> None:
        self.executor.shutdown()
