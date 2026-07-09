import asyncio
from abc import ABC, abstractmethod
from typing import TypeVar

from tqdm.asyncio import tqdm

from spimex_parser.logger import logger


T_IN = TypeVar("T_IN")


class BaseWorkerPool[T_IN](ABC):
    def __init__(
        self,
        in_queue: asyncio.Queue[T_IN | None],
        pbar: tqdm,  # type: ignore[implicit-any-type-argument]
        concurrency: int,
    ) -> None:
        self.in_queue = in_queue
        self.pbar = pbar
        self.concurrency = concurrency

        self._tasks: list[asyncio.Task[None]] = []

    def start(self) -> None:
        self._tasks = [asyncio.create_task(self._worker_loop()) for _ in range(self.concurrency)]

    async def stop(self) -> None:
        await self.in_queue.join()

        for _ in range(self.concurrency):
            await self.in_queue.put(None)

        await asyncio.gather(*self._tasks)

        await self._on_stop()

        self.pbar.refresh()

    async def _worker_loop(self) -> None:
        while True:
            item = await self.in_queue.get()

            if item is None:
                self.in_queue.task_done()
                return

            try:
                await self._process_item(item)
                self.pbar.update(1)
            except Exception:
                logger.exception("Необработанная ошибка в %s", type(self).__name__)
            finally:
                self.in_queue.task_done()

    @abstractmethod
    async def _process_item(self, item: T_IN) -> None:
        pass

    async def _on_stop(self) -> None:
        """Вызывается автоматически при остановке воркера."""
