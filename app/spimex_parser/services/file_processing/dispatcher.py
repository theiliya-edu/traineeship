from pathlib import Path
from typing import ClassVar

from spimex_parser.domain.dto import SpimexTradingResultDTO
from spimex_parser.domain.extractors import make_filedate_from_filename
from spimex_parser.logger import logger

from .base import FileProcessor, InvalidRowDetail
from .pdf_processor import PdfFileProcessor
from .xls_processor import XlsFileProcessor


class SpimexFileDispatcher:
    _PROCESSORS: ClassVar[dict[str, type[FileProcessor]]] = {
        ".pdf": PdfFileProcessor,
        ".xls": XlsFileProcessor,
    }

    def process_file(
        self,
        filebytes: bytes,
        filename: str,
    ) -> tuple[list[SpimexTradingResultDTO], list[InvalidRowDetail]]:
        suffix = Path(filename).suffix

        processor_cls = self._PROCESSORS.get(suffix)
        if not processor_cls:
            logger.info(f"Файл {filename!r} не обработан. Не поддерживаемый формат {suffix!r}")
            return [], []

        filedate = make_filedate_from_filename(filename)

        return processor_cls().process(filebytes, filedate)


def process_file(filebytes: bytes, filename: str) -> tuple[list[SpimexTradingResultDTO], list[InvalidRowDetail]]:
    dispatcher = SpimexFileDispatcher()
    return dispatcher.process_file(filebytes, filename)
