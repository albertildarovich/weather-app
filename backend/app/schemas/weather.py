from pydantic import BaseModel


class WeatherResponse(BaseModel):
    city: str
    country: str | None = None
    temperature: float
    wind_speed: float
    weather_code: int