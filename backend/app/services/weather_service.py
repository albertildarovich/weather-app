import httpx
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class CityNotFoundError(Exception):
    pass


class WeatherProviderError(Exception):
    pass


async def get_weather_by_city(
        city:str,
        client: httpx.AsyncClient,
) -> dict:
    logger.info("Fetching weather for city=%s", city)

    try:
        params = {
            "name": city,
            "count": 1,
            "language": "en",
            "format": "json",
        }
        
        geocoding_response = await client.get(
            settings.GEOCODING_API_URL,
            params=params,
        )

        logger.info("Geocoding URL: %s", geocoding_response.url)
        logger.info("Geocoding status: %s", geocoding_response.status_code)
        logger.info("Geocoding content type: %s", geocoding_response.headers.get("content-type"))
        logger.info("Geocoding response body: %s", geocoding_response.text[:500])

        geocoding_response.raise_for_status()

        geocoding_data = geocoding_response.json()
        locations = geocoding_data.get("results")

        if not locations:
            logger.warning("City not found: %s", city)
            raise CityNotFoundError(city)

        location = locations[0]

        weather_response = await client.get(
            settings.WEATHER_API_URL,
            params={
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "current": (
                    "temperature_2m,"
                    "wind_speed_10m,"
                    "weather_code"
                ),
            },
        )

        weather_response.raise_for_status()

        weather_data = weather_response.json()
        current = weather_data["current"]

        return {
            "city": location["name"],
            "country": location.get("country"),
            "temperature": current["temperature_2m"],
            "wind_speed": current["wind_speed_10m"],
            "weather_code": current["weather_code"],
        }

    except (
        httpx.HTTPError,
        KeyError,
        TypeError,
    ) as error:
        logger.exception(
            "Failed to fetch weather for city=%s",
            city,
        )
        raise WeatherProviderError() from error
