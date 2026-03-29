from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )
    USER_SERVICE_URL: AnyHttpUrl
    EVENT_SERVICE_URL: AnyHttpUrl
    SUB_SERVICE_URL: AnyHttpUrl

    REQUEST_TIMEOUT: float
    MAX_RETRIES: int
    RETRY_BACKOFF: float

    CB_FAIL_MAX: int = 5
    CB_TIMEOUT: int = 30

    JWT_SECRET: str
    ALGORITHM: str

    JWT_AUDIENCE: str = "gateway"


@lru_cache
def get_settings() -> Settings:
    return Settings()