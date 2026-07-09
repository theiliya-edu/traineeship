import asyncio
import itertools
from collections.abc import Callable, Coroutine

import aiohttp

from spimex_parser.logger import logger


async def fetch_text(client: aiohttp.ClientSession, proxy: str | None, url: str) -> str:
    async with client.get(url, proxy=proxy, raise_for_status=True) as response:
        return await response.text()


async def fetch_bytes(client: aiohttp.ClientSession, proxy: str | None, url: str) -> bytes:
    async with client.get(url, proxy=proxy, raise_for_status=True) as response:
        return await response.read()


class ResilientHttpClient:
    """Умный HTTP-клиент с поддержкой декартовой ротации прокси/UA и ретраями."""

    def __init__(
        self, user_agents: list[str], proxies: list[str | None], *, max_requests_per_session: int = 35
    ) -> None:
        self.max_requests_per_session = max_requests_per_session
        self.requests_served = 0

        self._lock = asyncio.Lock()
        self._background_tasks: set[asyncio.Task[None]] = set()

        self._combinations = itertools.cycle(itertools.product(proxies, user_agents))
        self.proxy, self.user_agent = next(self._combinations)
        self.session = self._create_session(self.user_agent)

    async def fetch_text(self, url: str) -> str:
        return await self._request_with_retry(url, lambda r: r.text())

    async def fetch_bytes(self, url: str) -> bytes:
        return await self._request_with_retry(url, lambda r: r.read())

    async def close(self) -> None:
        if self.session and not self.session.closed:
            await self.session.close()

    def _get_active_session(self) -> tuple[aiohttp.ClientSession, str | None]:
        """Возвращает сессию и прокси, плавно обновляя сессию по лимиту запросов."""
        if self.requests_served >= self.max_requests_per_session:
            old_session = self.session
            self.session = self._create_session(self.user_agent)
            self.requests_served = 0

            task = asyncio.create_task(self._close_delayed(old_session))
            self._background_tasks.add(task)
            task.add_done_callback(self._background_tasks.discard)

        self.requests_served += 1
        return self.session, self.proxy

    async def _force_rotate(self, current_bad_session: aiohttp.ClientSession) -> None:
        """Потокобезопасная ротация на следующую пару Proxy+UA при бане или ошибке."""
        async with self._lock:
            if self.session is not current_bad_session:
                return

            self.proxy, self.user_agent = next(self._combinations)

            logger.warning(
                "Обнаружена ошибка/бан! Ротация на новую комбинацию: Proxy=%s, UA=%s", self.proxy, self.user_agent
            )

            old_session = self.session
            task = asyncio.create_task(self._close_delayed(old_session))
            self._background_tasks.add(task)
            task.add_done_callback(self._background_tasks.discard)

            self.session = self._create_session(self.user_agent)
            self.requests_served = 0

    async def _request_with_retry[T](
        self,
        url: str,
        response_handler: Callable[[aiohttp.ClientResponse], Coroutine[None, None, T]],
    ) -> T:
        """Единый внутренний пайплайн выполнения запросов с логикой отказоустойчивости."""
        max_attempts = 3

        for attempt in range(1, max_attempts + 1):
            session, proxy = self._get_active_session()
            try:
                async with session.get(url, proxy=proxy, raise_for_status=True) as response:
                    return await response_handler(response)

            except aiohttp.ClientResponseError as e:
                if e.status in (403, 429, 503):
                    logger.error("Получен бан %s на url %s. Немедленная ротация.", e.status, url)
                    await self._force_rotate(current_bad_session=session)
                    continue
                logger.error("HTTP ошибка %s на url %s: %s", e.status, url, e.message)
                raise e

            except (TimeoutError, aiohttp.ClientError) as e:
                logger.warning("Сбой сети (%s) для %s (Попытка %d/%d)", type(e).__name__, url, attempt, max_attempts)

            if attempt == 2:
                logger.info("Простые ретраи исчерпаны для %s. Запускаем force_rotate.", url)
                await self._force_rotate(current_bad_session=session)

            if attempt < max_attempts:
                await asyncio.sleep(1.5)

        raise aiohttp.ClientError(f"Не удалось выполнить запрос после {max_attempts} попыток: {url}")

    @staticmethod
    def _create_session(user_agent: str) -> aiohttp.ClientSession:
        connector = aiohttp.TCPConnector(limit_per_host=10)
        headers = {
            "User-Agent": (
                f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) {user_agent}"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
                "application/signed-exchange;v=b3;q=0.7"
            ),
            "Accept-Language": "ru,en-US;q=0.9,en;q=0.8",
        }
        return aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=15),
            headers=headers,
        )

    @staticmethod
    async def _close_delayed(session: aiohttp.ClientSession) -> None:
        """Закрывает сессию с задержкой, чтобы завершились выполняющиеся запросы."""
        await asyncio.sleep(2.0)

        if not session.closed:
            await session.close()
