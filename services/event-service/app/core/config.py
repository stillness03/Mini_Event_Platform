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


@lru_cache
def get_settings() -> Settings:
    return Settings()
