from urllib.parse import urljoin

from pydantic import BaseModel

from shared.config import SharedSettings


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


class Settings(SharedSettings):
    client: ClientConfig = ClientConfig()
    spimex: SpimexConfig = SpimexConfig()


settings = Settings()
