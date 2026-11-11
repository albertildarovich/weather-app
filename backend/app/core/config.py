from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    APP_ENV: Literal["development", "production", "testing"] = "development"
    DEBUG: bool = False
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    HTTP_TIMEOUT: float = 10.0
    HTTP_MAX_CONNECTIONS: int = 100

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    GEOCODING_API_URL: str = (
    "https://geocoding-api.open-meteo.com/v1/search"
    )

    WEATHER_API_URL: str = (
        "https://api.open-meteo.com/v1/forecast"
    )


settings = Settings()