import asyncio
import datetime
from zoneinfo import ZoneInfo

import aiohttp
from tqdm.asyncio import tqdm

from spimex_parser.config import settings
from spimex_parser.domain.extractors import extract_date_from_download_url, extract_download_urls_from_page
from spimex_parser.infrastructure.http_client import ResilientHttpClient
from spimex_parser.logger import logger


class LinkPaginator:
    def __init__(
        self,
        start_date: datetime.date,
        urls_queue: asyncio.Queue[str | None],
        http_client: ResilientHttpClient,
        pbars: list[tqdm],  # type: ignore[implicit-any-type-argument]
    ) -> None:
        self.start_date = start_date
        self.urls_queue = urls_queue
        self.http_client = http_client
        self.pbars = pbars

    async def execute(self) -> None:
        current_date = datetime.datetime.now(ZoneInfo("Europe/Moscow")).date()
        if self.start_date > current_date:
            return

        await self._run_pagination_loop()

    async def _run_pagination_loop(self) -> None:
        page_number = 1
        while True:
            page_url = f"{settings.spimex.trades_result_url}?page=page-{page_number}"

            try:
                html = await self.http_client.fetch_text(page_url)
            except (TimeoutError, aiohttp.ClientError):
                logger.exception("Финальная ошибка скачивания (все попытки и прокси исчерпаны): %s", page_url)
                continue

            discovered_urls = extract_download_urls_from_page(html)
            filtered_urls, should_stop = self.filter_urls(discovered_urls)

            if not filtered_urls:
                return

            self._update_progress_bars(len(filtered_urls))

            for url in filtered_urls:
                await self.urls_queue.put(url)

            if should_stop:
                return

            page_number += 1

    def filter_urls(self, urls: list[str]) -> tuple[list[str], bool]:
        if not urls:
            return [], True

        filtered = [
            url for url in urls if (date := extract_date_from_download_url(url)) is not None and date > self.start_date
        ]
        should_stop = len(urls) != len(filtered)

        return filtered, should_stop

    def _update_progress_bars(self, count: int) -> None:
        for pbar in self.pbars:
            pbar.total += count

            if pbar.n == 0:
                pbar.refresh()
