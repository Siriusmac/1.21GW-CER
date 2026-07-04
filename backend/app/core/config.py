from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "1.21GW-CER"
    database_url: str = "postgresql+psycopg://cer:cer@localhost:5432/cer"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    timezone: str = "Europe/Rome"
    default_granularity_minutes: int = 15
    incentive_eur_kwh: float = 0.11

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
