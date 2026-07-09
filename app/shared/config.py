from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent


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


class SharedSettings(BaseSettings):
    db: Annotated[DBConfig, Field(..., validation_alias="SHARED__DB")]

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file=BASE_DIR / ".env",
        extra="ignore",
    )


settings = SharedSettings()
