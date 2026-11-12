import httpx
import pytest

from unittest.mock import AsyncMock
from fastapi.testclient import TestClient

from app.main import app
from app.dependencies.http import get_http_client


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def weather_api(monkeypatch):
    mock_client = AsyncMock(spec=httpx.AsyncClient)

    monkeypatch.setitem(
        app.dependency_overrides,
        get_http_client,
        lambda: mock_client,
    )

    with TestClient(app) as test_client:
        yield test_client, mock_client
