import httpx
import pytest
from unittest.mock import AsyncMock

from app.core.config import settings
from app.services.weather_service import (
    get_weather_by_city,
    CityNotFoundError,
    WeatherProviderError,
)


@pytest.mark.asyncio
async def test_get_weather_by_city_success():
    geocoding_response = httpx.Response(
        200,
        json={
            "results": [
                {
                    "name": "Berlin",
                    "country": "Germany",
                    "latitude": 52.52,
                    "longitude": 13.41,
                }
            ]
        },
        request=httpx.Request(
            "GET",
            settings.GEOCODING_API_URL,
        ),
    )

    weather_response = httpx.Response(
        200,
        json={
            "current": {
                "temperature_2m": 18.5,
                "wind_speed_10m": 12.3,
                "weather_code": 1,
            }
        },
        request=httpx.Request(
            "GET",
            settings.WEATHER_API_URL,
        ),
    )

    mock_client = AsyncMock(spec=httpx.AsyncClient)

    mock_client.get.side_effect = [
        geocoding_response,
        weather_response,
    ]

    result = await get_weather_by_city(
        "Berlin",
        mock_client,
    )

    assert result == {
        "city": "Berlin",
        "country": "Germany",
        "temperature": 18.5,
        "wind_speed": 12.3,
        "weather_code": 1,
    }

    assert mock_client.get.await_count == 2


@pytest.mark.asyncio
async def test_get_weather_by_city_not_found():
    geocoding_response = httpx.Response(
        200,
        json={"results": []},
        request=httpx.Request(
            "GET",
            settings.GEOCODING_API_URL,
        ),
    )

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.return_value = geocoding_response

    with pytest.raises(CityNotFoundError):
        await get_weather_by_city(
            "UnknownCity",
            mock_client,
        )

    assert mock_client.get.await_count == 1


@pytest.mark.asyncio
async def test_get_weather_by_city_provider_error():
    error_response = httpx.Response(
        503,
        request=httpx.Request(
            "GET",
            settings.GEOCODING_API_URL,
        ),
    )

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.return_value = error_response

    with pytest.raises(WeatherProviderError):
        await get_weather_by_city(
            "Berlin",
            mock_client,
        )

    assert mock_client.get.await_count == 1


@pytest.mark.asyncio
async def test_get_weather_by_city_weather_api_error():
    geocoding_response = httpx.Response(
        200,
        json={
            "results": [
                {
                    "name": "Berlin",
                    "country": "Germany",
                    "latitude": 52.52,
                    "longitude": 13.41,
                }
            ]
        },
        request=httpx.Request(
            "GET",
            settings.GEOCODING_API_URL,
        ),
    )

    weather_error_response = httpx.Response(
        500,
        json={"error": "Internal Server Error"},
        request=httpx.Request(
            "GET",
            settings.WEATHER_API_URL,
        ),
    )

    mock_client = AsyncMock(spec=httpx.AsyncClient)

    mock_client.get.side_effect = [
        geocoding_response,
        weather_error_response,
    ]

    with pytest.raises(WeatherProviderError):
        await get_weather_by_city(
            "Berlin",
            mock_client,
        )

    assert mock_client.get.await_count == 2