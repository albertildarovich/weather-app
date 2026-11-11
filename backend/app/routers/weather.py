import httpx

from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies.http import get_http_client

from app.schemas.weather import WeatherResponse
from app.services.weather_service import (
    CityNotFoundError,
    WeatherProviderError,
    get_weather_by_city,
)


router = APIRouter()


@router.get("", response_model=WeatherResponse)
async def get_weather(
    city: str = Query(..., min_length=1),
    client: httpx.AsyncClient = Depends(get_http_client)
):
    try:
        return await get_weather_by_city(city, client)

    except CityNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"City '{city}' not found",
        )

    except WeatherProviderError:
        raise HTTPException(
            status_code=502,
            detail="Weather service is temporarily unavailable",
        )