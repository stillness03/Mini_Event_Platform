from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )

    # Mongo
    MONGO_URI: str
    DB_NAME: str

    # Business rules
    MAX_EVENTS_PER_HOUR: int = 5

    # Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    REDIS_MAX_CONNECTIONS: int = 50
    REDIS_SOCKET_TIMEOUT: int = 5
    REDIS_SOCKET_CONNECT_TIMEOUT: int = 5
    
    # Cache TTL
    CACHE_DEFAULT_TTL: int = 300
    CACHE_EVENT_TTL: int = 600
    CACHE_USER_EVENTS_TTL: int = 120


@lru_cache
def get_settings() -> Settings:
    return Settings()
