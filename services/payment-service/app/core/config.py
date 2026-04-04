from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    PROJECT_NAME: str = "payment-service"
    DOMAIN: str = "payment-service.io"

    STRIPE_SECRET_KEY: str
    STRIPE_PUBLIC_KEY: str
    STRIPE_WEBHOOK_SECRET: str

    DEFAULT_PAYMENT_PROVIDER: str = 'stripe'

    DATABASE_URL: str

    EVENT_SERVICE_URL: str

@lru_cache
def get_settings() -> Settings:
    return Settings()
