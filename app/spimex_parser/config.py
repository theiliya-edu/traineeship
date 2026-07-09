from pathlib import Path
from urllib.parse import urljoin

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class SpimexConfig(BaseModel):
    root_url: str = "https://spimex.com/"
    path_url: str = "/markets/oil_products/trades/results/"

    @property
    def trades_result_url(self) -> str:
        return urljoin(self.root_url, self.path_url)


class ClientConfig(BaseModel):
    user_agents: list[str] = [
        "Chrome/135.0.0.0 Safari/537.36",
        "Chrome/148.0.0.0 Safari/537.36",
        "Chrome/149.0.0.0 Safari/537.36",
    ]
    proxies: list[str | None] = [
        None,
        "http://185.200.188.234:10001",
        "http://84.47.150.125:1080",
    ]


class DBConfig(BaseModel):
    user: str
    password: str
    host: str
    port: int
    name: str

    @property
    def async_url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    @property
    def sync_url(self) -> str:
        return f"postgresql+psycopg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class Settings(BaseSettings):
    db: DBConfig
    client: ClientConfig = ClientConfig()
    spimex: SpimexConfig = SpimexConfig()

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_nested_delimiter="__",
        env_file=BASE_DIR / ".env",
        extra="ignore",
    )


settings = Settings()
