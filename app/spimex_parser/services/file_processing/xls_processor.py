import datetime
from typing import override

import xlrd
from pydantic import ValidationError

from spimex_parser.domain.dto import SpimexTradingResultDTO

from .base import FileProcessor, InvalidRowDetail


class XlsFileProcessor(FileProcessor):
    TABLE_POINTER = "Единица измерения: Метрическая тонна".lower()

    @override
    def process(
        self,
        filebytes: bytes,
        filedate: datetime.date,
    ) -> tuple[list[SpimexTradingResultDTO], list[InvalidRowDetail]]:
        valid_dtos: list[SpimexTradingResultDTO] = []
        invalid_rows: list[InvalidRowDetail] = []

        sheet = xlrd.open_workbook(file_contents=filebytes).sheet_by_index(0)
        table_start_index = 0

        for i in range(sheet.nrows):
            row = sheet.row_values(i)

            if row[1].lower() == self.TABLE_POINTER:
                table_start_index = i + 3
                break

        for index in range(table_start_index, sheet.nrows):
            row = sheet.row_values(index)

            if row[1].lower() == "итого:":
                break

            if row[1] and not row[2]:
                continue

            if row[-1] == "-":
                continue

            try:
                dto = SpimexTradingResultDTO.from_row(row[1:], filedate)
                valid_dtos.append(dto)
            except (ValidationError, TypeError, IndexError) as e:
                invalid_rows.append(InvalidRowDetail(index=index, row=list(row), error=e))

        return valid_dtos, invalid_rows
