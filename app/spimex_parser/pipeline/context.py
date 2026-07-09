from __future__ import annotations

import asyncio
import sys
from dataclasses import dataclass

from tqdm.asyncio import tqdm

from spimex_parser.domain.dto import SpimexTradingResultDTO


@dataclass(slots=True)
class DownloadedFile:
    content: bytes
    name: str


@dataclass
class ProgressBars:
    download: tqdm  # type: ignore[implicit-any-type-argument]
    cpu: tqdm  # type: ignore[implicit-any-type-argument]
    db: tqdm  # type: ignore[implicit-any-type-argument]

    @classmethod
    def create(cls) -> ProgressBars:
        return cls(
            download=tqdm(
                desc="1. Скачивание файлов",
                total=0,
                unit="file",
                leave=True,
                file=sys.stdout,
                mininterval=1,
                dynamic_ncols=True,
            ),
            cpu=tqdm(
                desc="2. Обработка файлов ",
                total=0,
                unit="file",
                leave=True,
                file=sys.stdout,
                mininterval=1,
                dynamic_ncols=True,
            ),
            db=tqdm(
                desc="3. Запись в БД      ",
                total=0,
                unit="file",
                leave=True,
                file=sys.stdout,
                mininterval=1,
                dynamic_ncols=True,
            ),
        )

    def close_all(self) -> None:
        self.download.close()
        self.cpu.close()
        self.db.close()


@dataclass
class Queues:
    url: asyncio.Queue[str | None]
    file: asyncio.Queue[DownloadedFile | None]
    db: asyncio.Queue[list[SpimexTradingResultDTO] | None]

    @classmethod
    def create(cls, maxsize: int = 0) -> Queues:
        return cls(
            url=asyncio.Queue(maxsize=maxsize),
            file=asyncio.Queue(maxsize=maxsize),
            db=asyncio.Queue(maxsize=maxsize),
        )
