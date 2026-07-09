# pyright: reportCallIssue=false

import logging
from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("spimex-parser")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMP_FOLDER = BASE_DIR / "temp"
PROXIES = {"http": "http://185.200.188.234:10001"}


class DBConfig(BaseModel):
    user: str
    password: str
    host: str
    port: int
    name: str

    @property
    def url(self) -> str:
        return f"postgresql+psycopg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class Settings(BaseSettings):
    db: DBConfig

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_nested_delimiter="__",
        env_file=BASE_DIR / ".env",
        extra="ignore",
    )


settings = Settings()
