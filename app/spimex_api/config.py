from typing import Annotated

from pydantic import BaseModel, Field

from shared.config import SharedSettings


class RedisConfig(BaseModel):
    host: str
    port: int = 6379
    db: int = 0
    ttl: int = 3600

    @property
    def url(self) -> str:
        return f"redis://{self.host}:{self.port}/{self.db}"


class Settings(SharedSettings):
    redis: Annotated[RedisConfig, Field(..., validation_alias="SPIMEX_API__REDIS")]


settings = Settings()
