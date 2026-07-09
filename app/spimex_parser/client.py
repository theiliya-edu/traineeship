import datetime
from pathlib import Path

import requests

from spimex_parser.config import PROXIES, TEMP_FOLDER
from spimex_parser.extractors import (
    extract_date_from_download_url,
    extract_download_urls_from_page,
    make_file_name_from_download_url,
)

session = requests.Session()

session.headers.update(
    {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/149.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
            "application/signed-exchange;v=b3;q=0.7"
        ),
        "Accept-Language": "ru,en-US;q=0.9,en;q=0.8",
    }
)


def fetch_spimex_download_urls(start_date: datetime.date) -> list[str]:
    if start_date > datetime.datetime.now(datetime.UTC).date():
        return []

    download_urls: list[str] = []
    page = 1

    while True:
        url = f"https://spimex.com/markets/oil_products/trades/results/?page=page-{page}"
        html = fetch_html(url)
        page += 1

        discovered_urls = extract_download_urls_from_page(html)

        if not discovered_urls:
            break

        filtered_urls = [link for link in discovered_urls if extract_date_from_download_url(link) >= start_date]

        if not filtered_urls:
            break

        download_urls += filtered_urls

    return download_urls


def fetch_html(url: str) -> str:
    response = session.get(url, proxies=PROXIES)

    return response.text


def download_file(url: str) -> Path:
    """Download the file and return the full path to the saved file."""

    response = session.get(url, proxies=PROXIES)
    response.raise_for_status()

    file_name = make_file_name_from_download_url(url)
    path_to_file = TEMP_FOLDER / file_name

    with open(TEMP_FOLDER / file_name, "wb") as file:
        file.write(response.content)

    return path_to_file
