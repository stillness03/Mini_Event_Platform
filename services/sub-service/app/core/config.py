from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )

    SUB_DATABASE_URL: str
    EVENT_SERVICE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    LOG_LEVEL: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()

