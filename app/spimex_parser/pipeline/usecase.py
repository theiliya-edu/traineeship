import datetime

from shared.database.helper import SessionFactory
from spimex_parser.config import settings
from spimex_parser.infrastructure.http_client import ResilientHttpClient
from spimex_parser.pipeline.context import ProgressBars, Queues
from spimex_parser.pipeline.workers import (
    DownloadWorkerPool,
    LinkPaginator,
    ProcessFileWorkerPool,
    SaveWorkerPool,
)


class DownloadContentSinceDateUseCase:
    def __init__(self, start_date: datetime.date) -> None:
        self.start_date = start_date

    async def execute(self) -> None:
        queues = Queues.create()
        pbars = ProgressBars.create()
        http_client = ResilientHttpClient(
            user_agents=settings.client.user_agents,
            proxies=settings.client.proxies,
        )

        link_paginator = LinkPaginator(
            self.start_date,
            queues.url,
            http_client,
            [pbars.download, pbars.cpu, pbars.db],
        )

        download_worker_pool = DownloadWorkerPool(
            queues.url,
            queues.file,
            http_client,
            pbars.download,
            concurrency=5,
        )

        save_worker_pool = SaveWorkerPool(
            queues.db,
            SessionFactory,
            pbars.db,
            concurrency=2,
        )

        process_file_executor = ProcessFileWorkerPool(
            queues.file,
            queues.db,
            pbars.cpu,
            concurrency=5,
        )

        save_worker_pool.start()
        process_file_executor.start()
        download_worker_pool.start()

        await link_paginator.execute()

        await download_worker_pool.stop()
        await process_file_executor.stop()
        await save_worker_pool.stop()

        await http_client.close()
        pbars.close_all()
