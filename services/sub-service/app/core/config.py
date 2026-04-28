from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from functools import lru_cache
from pydantic import computed_field


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

    @computed_field
    @property
    def ALEMBIC_DATABASE_URL(self) -> str:
        return self.SUB_DATABASE_URL.replace(
            "postgresql+asyncpg", "postgresql+psycopg"
        )

@lru_cache
def get_settings() -> Settings:
    return Settings()

