from dataclasses import dataclass
from pathlib import Path

import pdfplumber
import xlrd
from pydantic import ValidationError

from spimex_parser.config import logger
from spimex_parser.dto import SpimexTradingResultDTO
from spimex_parser.extractors import extract_date_from_path_to_file


@dataclass(frozen=True)
class InvalidRowDetail:
    index: int
    row: list[str | None]  # pdfplumber может возвращать None в ячейках
    error: ValidationError | TypeError | IndexError


TABLE_POINTER = "Единица измерения: Метрическая тонна".lower()


def process_file(
    path_to_file: Path,
) -> tuple[list[SpimexTradingResultDTO], list[InvalidRowDetail]]:
    available_extractor = {
        ".pdf": process_pdf,
        ".xls": process_xls,
    }

    extractor = available_extractor.get(path_to_file.suffix)

    if not extractor:
        logger.info(f"Файл {path_to_file.name!r} не обработан. Не поддерживаемый формат {path_to_file.suffix!r}")
        return [], []

    result: tuple[list[SpimexTradingResultDTO], list[InvalidRowDetail]] = extractor(path_to_file)

    return result


def process_pdf(
    path_to_file: Path,
) -> tuple[list[SpimexTradingResultDTO], list[InvalidRowDetail]]:
    valid_dtos: list[SpimexTradingResultDTO] = []
    invalid_rows: list[InvalidRowDetail] = []
    date = extract_date_from_path_to_file(path_to_file)

    with pdfplumber.open(path_to_file) as pdf:
        for index, page in enumerate(pdf.pages):
            table = page.extract_table()

            if not table:
                continue

            table = table[2:] if index == 0 else table

            for row in table:
                if row and row[-1] != "-":
                    clean_row = list(map(str, row))
                    try:
                        dto = SpimexTradingResultDTO.from_row(clean_row, date)
                        valid_dtos.append(dto)
                    except (ValidationError, TypeError, IndexError) as e:
                        invalid_rows.append(InvalidRowDetail(index=index, row=row, error=e))

    return valid_dtos, invalid_rows


def process_xls(
    path_to_file: Path,
) -> tuple[list[SpimexTradingResultDTO], list[InvalidRowDetail]]:
    valid_dtos: list[SpimexTradingResultDTO] = []
    invalid_rows: list[InvalidRowDetail] = []
    date = extract_date_from_path_to_file(path_to_file)

    sheet = xlrd.open_workbook(str(path_to_file)).sheet_by_index(0)
    table_start_index = 0

    for i in range(sheet.nrows):
        row = sheet.row_values(i)

        if row[1].lower() == TABLE_POINTER:
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
            dto = SpimexTradingResultDTO.from_row(row[1:], date)
            valid_dtos.append(dto)
        except (ValidationError, TypeError, IndexError) as e:
            invalid_rows.append(InvalidRowDetail(index=index, row=list(row), error=e))

    return valid_dtos, invalid_rows
