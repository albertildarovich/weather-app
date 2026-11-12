import httpx

def make_response(status_code, json_data, url):
    return httpx.Response(
        status_code,
        json=json_data,
        request=httpx.Request("GET", url),
    )


def test_root_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Weather API!"}


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_weather_success(weather_api):
    client, mock_client = weather_api

    geocoding_response = make_response(
        200,
        {
            "results": [
                {
                    "name": "Berlin",
                    "country": "Germany",
                    "latitude": 52.52,
                    "longitude": 13.41,
                }
            ]
        },
        "https://geocoding.test",
    )

    weather_response = make_response(
        200,
        {
            "current": {
                "temperature_2m": 18.5,
                "wind_speed_10m": 12.3,
                "weather_code": 1,
            }
        },
        "https://weather.test",
    )

    mock_client.get.side_effect = [
        geocoding_response,
        weather_response,
    ]

    response = client.get("/weather?city=Berlin")

    assert response.status_code == 200

    assert response.json() == {
        "city": "Berlin",
        "country": "Germany",
        "temperature": 18.5,
        "wind_speed": 12.3,
        "weather_code": 1,
    }

    assert mock_client.get.await_count == 2


def test_get_weather_city_not_found(weather_api):
    client, mock_client = weather_api

    geocoding_response = make_response(
        200,
        {"results": []},
        "https://geocoding.test",
    )

    mock_client.get.return_value = geocoding_response

    response = client.get("/weather?city=UnknownCity")

    assert response.status_code == 404

    assert response.json() == {"detail": "City 'UnknownCity' not found"}

    assert mock_client.get.await_count == 1


def test_get_weather_provider_error(weather_api):
    client, mock_client = weather_api

    geocoding_response = make_response(
        200,
        {
            "results": [
                {
                    "name": "Berlin",
                    "country": "Germany",
                    "latitude": 52.52,
                    "longitude": 13.41,
                }
            ]
        },
        "https://geocoding.test",
    )

    weather_error_response = make_response(
        500,
        {"error": "Internal Server Error"},
        "https://weather.test",
    )

    mock_client.get.side_effect = [
        geocoding_response,
        weather_error_response,
    ]

    response = client.get("/weather?city=Berlin")

    assert response.status_code == 502

    assert response.json() == {"detail": "Weather service is temporarily unavailable"}

    assert mock_client.get.await_count == 2


def test_get_weather_without_city(client):
    response = client.get("/weather")

    assert response.status_code == 422


def test_get_weather_with_empty_city(client):
    response = client.get("/weather?city=")

    assert response.status_code == 422

def test_get_weather_missing_current(weather_api):
    client, mock_client = weather_api

    geocoding_response = make_response(
        200,
        {
            "results": [
                {
                    "name": "Berlin",
                    "country": "Germany",
                    "latitude": 52.52,
                    "longitude": 13.41,
                }
            ]
        },
        "https://geocoding.test",
    )

    weather_response = make_response(
        200,
        {
            "latitude": 52.52,
            "longitude": 13.41,
        },
        "https://weather.test",
    )

    mock_client.get.side_effect = [
        geocoding_response,
        weather_response,
    ]

    response = client.get("/weather?city=Berlin")

    assert response.status_code == 502
    assert response.json() == {
        "detail": "Weather service is temporarily unavailable"
    }

def test_get_weather_invalid_json(weather_api):
    client, mock_client = weather_api

    geocoding_response = make_response(
        200,
        {
            "results": [
                {
                    "name": "Berlin",
                    "country": "Germany",
                    "latitude": 52.52,
                    "longitude": 13.41,
                }
            ]
        },
        "https://geocoding.test",
    )

    weather_response = httpx.Response(
        200,
        text="Something went wrong",
        request=httpx.Request(
            "GET",
            "https://weather.test",
        ),
    )

    mock_client.get.side_effect = [
        geocoding_response,
        weather_response,
    ]

    response = client.get("/weather?city=Berlin")

    assert response.status_code == 502
    assert response.json() == {
        "detail": "Weather service is temporarily unavailable"
    }


def test_metrics_endpoint(client):
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
