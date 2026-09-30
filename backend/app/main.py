import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.api.health import health_check
from app.api.v1.api import api_router
from app.core.config import settings
from app.services.order_cache import order_cache


class InstanceIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Instance-ID"] = settings.INSTANCE_ID
        return response


class Lab3DelayMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        if settings.LAB3_DELAY_MS > 0:
            await asyncio.sleep(settings.LAB3_DELAY_MS / 1000)
        return await call_next(request)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.DEBUG:
        print("\n" + "=" * 50)
        print(f"🚀 Swagger UI: http://localhost:8000{app.docs_url}")
        print("🔗 API Base:   http://localhost:8000/api/v1")
        print("=" * 50 + "\n")
    try:
        yield
    finally:
        await order_cache.close()


app = FastAPI(
    title="LogiFlow",
    openapi_url="/openapi.json" if settings.DEBUG else None,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

app.add_middleware(InstanceIdMiddleware)
app.add_middleware(Lab3DelayMiddleware)

if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=[
            "Content-Type",
            "Authorization",
            "Accept",
            "X-Requested-With",
        ],
    )

app.include_router(api_router, prefix="/api/v1")
app.add_api_route("/health", health_check, methods=["GET"])
