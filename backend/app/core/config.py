from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from typing import Literal
from pathlib import Path


ENV_FILE = Path(__file__).resolve().parents[3] / ".env"

class Settings(BaseSettings):
    APP_ENV: Literal["development", "production", "testing"] = "development"
    DEBUG: bool = False
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    HTTP_TIMEOUT: float = 10.0
    HTTP_MAX_CONNECTIONS: int = 100

    DATABASE_URL: str

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int

    GEOCODING_API_URL: str = (
    "https://geocoding-api.open-meteo.com/v1/search"
    )

    WEATHER_API_URL: str = (
        "https://api.open-meteo.com/v1/forecast"
    )

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
    )

    @model_validator(mode="after")
    def validate_debug_mode(self) -> "Settings":
        if self.APP_ENV == "production" and self.DEBUG:
            raise ValueError(
                "DEBUG must be false in production"
            )

        return self


settings = Settings()  # pyright: ignore[reportCallIssue]