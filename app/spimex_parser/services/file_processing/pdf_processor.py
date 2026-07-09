import datetime
import io
from typing import override

import pdfplumber
from pydantic import ValidationError

from spimex_parser.domain.dto import SpimexTradingResultDTO

from .base import FileProcessor, InvalidRowDetail


class PdfFileProcessor(FileProcessor):
    @override
    def process(
        self,
        filebytes: bytes,
        filedate: datetime.date,
    ) -> tuple[list[SpimexTradingResultDTO], list[InvalidRowDetail]]:
        valid_dtos: list[SpimexTradingResultDTO] = []
        invalid_rows: list[InvalidRowDetail] = []

        file_obj = io.BytesIO(filebytes)

        with pdfplumber.open(file_obj) as pdf:
            for index, page in enumerate(pdf.pages):
                table = page.extract_table()

                if not table:
                    continue

                table = table[2:] if index == 0 else table

                for row in table:
                    if row and row[-1] != "-":
                        clean_row = list(map(str, row))
                        try:
                            dto = SpimexTradingResultDTO.from_row(clean_row, filedate)
                            valid_dtos.append(dto)
                        except (ValidationError, TypeError, IndexError) as e:
                            invalid_rows.append(InvalidRowDetail(index=index, row=row, error=e))

        return valid_dtos, invalid_rows
