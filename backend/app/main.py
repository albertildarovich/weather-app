import time
import httpx
import logging

logger = logging.getLogger(__name__)

from fastapi import Request, Response, FastAPI
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.core.metrics import (
    REQUEST_COUNT,
    REQUEST_LATENCY,
    REQUESTS_IN_PROGRESS,
)

from contextlib import asynccontextmanager

from app.routers import weather
from app.core.logging_config import setup_logging

from app.core.config import settings

setup_logging(settings.LOG_LEVEL)

logger.debug("Debug logging is enabled")
logger.info("Application environment: %s", settings.APP_ENV)
logger.warning("This is a test warning")

logger.info("Application environment: %s", settings.APP_ENV)

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient(
        timeout=settings.HTTP_TIMEOUT,
        limits=httpx.Limits(
            max_connections=settings.HTTP_MAX_CONNECTIONS
        ),
    )

    yield

    await app.state.http_client.aclose()



app = FastAPI(
    title="Weather API",
    description="Backend для приложения погоды",
    version="1.0.0",
    lifespan=lifespan,
    debug=settings.DEBUG
)

@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    if request.url.path == "/metrics":
        return await call_next(request)

    method = request.method
    endpoint = request.url.path

    REQUESTS_IN_PROGRESS.labels(
        method=method,
        endpoint=endpoint,
    ).inc()

    start_time = time.perf_counter()
    status_code = 500

    try:
        response = await call_next(request)
        status_code = response.status_code
        return response

    finally:
        duration = time.perf_counter() - start_time

        REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            http_status=str(status_code),
        ).inc()

        REQUEST_LATENCY.labels(
            method=method,
            endpoint=endpoint,
        ).observe(duration)

        REQUESTS_IN_PROGRESS.labels(
            method=method,
            endpoint=endpoint,
        ).dec()


app.include_router(
    weather.router,
    prefix="/weather",
    tags=["Weather"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to Weather API!"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/metrics", include_in_schema=False)
async def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )