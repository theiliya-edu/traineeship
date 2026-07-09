import datetime
import re
from pathlib import Path
from urllib.parse import urljoin


def extract_download_urls_from_page(html: str) -> list[str]:
    pattern = r'href="(/files/trades/result/[^"\s>]+)'

    discovered_urls = [urljoin("https://spimex.com/", url) for url in re.findall(pattern, html)]

    return discovered_urls


def extract_date_from_download_url(url: str) -> datetime.date:
    path = url.split("?", maxsplit=1)[0]
    file_name = path.rsplit("/", maxsplit=1)[1]
    date_str = file_name.rsplit("_", maxsplit=1)[1][:8]

    date = datetime.datetime.strptime(date_str, "%Y%m%d").date()

    return date


def make_file_name_from_download_url(url: str) -> str:
    path = url.split("?", maxsplit=1)[0]
    file_name = path.rsplit("/", maxsplit=1)[1]

    date_str = file_name.rsplit("_", maxsplit=1)[1][:8]
    extension = file_name.rsplit(".", maxsplit=1)[1]

    return f"{date_str}.{extension}"


def extract_date_from_path_to_file(path: Path) -> datetime.date:
    date = datetime.datetime.strptime(path.stem, "%Y%m%d").date()

    return date
