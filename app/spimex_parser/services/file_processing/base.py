import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass

from pydantic import ValidationError

from spimex_parser.domain.dto import SpimexTradingResultDTO


@dataclass(frozen=True)
class InvalidRowDetail:
    index: int
    row: list[str | None]
    error: ValidationError | TypeError | IndexError


class FileProcessor(ABC):
    @abstractmethod
    def process(
        self,
        filebytes: bytes,
        filedate: datetime.date,
    ) -> tuple[list[SpimexTradingResultDTO], list[InvalidRowDetail]]:
        pass
