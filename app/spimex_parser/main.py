import datetime
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

from tqdm import tqdm

from spimex_parser.client import (
    download_file,
    fetch_spimex_download_urls,
)
from spimex_parser.config import TEMP_FOLDER, logger
from spimex_parser.database.repository import save_in_db
from spimex_parser.dto import SpimexTradingResultDTO
from spimex_parser.parsers import process_file


def download_and_parse_worker(url: str) -> list[SpimexTradingResultDTO]:
    try:
        path_to_file = download_file(url)

        entries, errors = process_file(path_to_file)

        if errors:
            logger.warning(f"Файл {path_to_file.name} обработан с предупреждениями. Ошибок строки: {len(errors)}")
            for detail in errors:
                logger.error(
                    f"[{path_to_file.suffix.upper()}] Ошибка в {path_to_file.name} на строке #{detail.index}. "
                    + f"Причина: {detail.error} | Данные: {detail.row}"
                )

        path_to_file.unlink(missing_ok=True)

        return entries
    except Exception as e:
        logger.error(f"Ошибка при обработке ссылки {url!r}: {e}")
        return []


def entry() -> None:
    os.makedirs(TEMP_FOLDER, exist_ok=True)

    logger.info("Получаем ссылки для загрузки файлов...")
    urls = fetch_spimex_download_urls(datetime.datetime.strptime("20230101", "%Y%m%d").date())
    logger.info(f"Получено ссылок: {len(urls)} шт.")

    all_dtos: list[SpimexTradingResultDTO] = []

    st = time.time()

    with ProcessPoolExecutor() as executor:
        futures = {executor.submit(download_and_parse_worker, url): url for url in urls}

        start_log_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_prefix = f"{start_log_time} [INFO] Обрабатываем файлы"

        for future in tqdm(as_completed(futures), total=len(urls), desc=log_prefix):
            entries = future.result()
            all_dtos.extend(entries)

    et = time.time()

    logger.info(f"Обработка всех файлов завершена за {round(et - st, 2)}с. Всего строк: {len(all_dtos)}.")

    if all_dtos:
        logger.info("Начинаем сохранение в БД...")
        save_in_db(all_dtos)
        logger.info("Данные сохранены.")


if __name__ == "__main__":
    entry()
