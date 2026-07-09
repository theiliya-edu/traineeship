import asyncio
from typing import override

import aiohttp
from tqdm.asyncio import tqdm

from spimex_parser.domain.extractors import make_file_name_from_download_url
from spimex_parser.infrastructure.http_client import ResilientHttpClient
from spimex_parser.logger import logger
from spimex_parser.pipeline.context import DownloadedFile
from spimex_parser.pipeline.workers.base import BaseWorkerPool


class DownloadWorkerPool(BaseWorkerPool[str]):
    def __init__(
        self,
        urls_queue: asyncio.Queue[str | None],
        files_queue: asyncio.Queue[DownloadedFile | None],
        http_client: ResilientHttpClient,
        pbar: tqdm,  # type: ignore[implicit-any-type-argument]
        *,
        concurrency: int = 5,
    ) -> None:
        super().__init__(urls_queue, pbar, concurrency)

        self.files_queue = files_queue
        self.http_client = http_client

    @override
    async def _process_item(self, item: str) -> None:
        try:
            filebytes = await self.http_client.fetch_bytes(item)
        except (TimeoutError, aiohttp.ClientError):
            logger.exception("Финальная ошибка скачивания (все попытки и прокси исчерпаны): %s", item)
            return

        filename = make_file_name_from_download_url(item)

        if filename is None:
            return

        file = DownloadedFile(filebytes, filename)

        await self.files_queue.put(file)
