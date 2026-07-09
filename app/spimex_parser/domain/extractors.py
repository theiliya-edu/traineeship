import datetime
import re
from pathlib import Path
from urllib.parse import urljoin

from spimex_parser.config import settings


def extract_download_urls_from_page(html: str) -> list[str]:
    pattern = r'href="(/files/trades/result/[^"\s>]+)'

    discovered_urls = [urljoin(settings.spimex.root_url, url) for url in re.findall(pattern, html)]

    return discovered_urls


def extract_date_from_download_url(url: str) -> datetime.date:
    url_path = url.split("?", maxsplit=1)[0]
    file_name = url_path.rsplit("/", maxsplit=1)[1]  # IndexError
    date_str = file_name.rsplit("_", maxsplit=1)[1][:8]  # IndexError

    date = datetime.datetime.strptime(date_str, "%Y%m%d").date()  # ValueError

    return date


def make_file_name_from_download_url(url: str) -> str:
    path = url.split("?", maxsplit=1)[0]
    filename = path.rsplit("/", maxsplit=1)[1]  # IndexError

    name = filename.rsplit("_", maxsplit=1)[1][:8]  # IndexError
    suffix = filename.rsplit(".", maxsplit=1)[1]  # IndexError

    return f"{name}.{suffix}"


def make_filedate_from_filename(filename: str) -> datetime.date:
    date = datetime.datetime.strptime(Path(filename).stem, "%Y%m%d").date()  # ValueError

    return date
