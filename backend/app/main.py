from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.DEBUG:
        print("\n" + "=" * 50)
        print(f"🚀 Swagger UI: http://localhost:8000{app.docs_url}")
        print("🔗 API Base:   http://localhost:8000/api/v1")
        print("=" * 50 + "\n")
    yield


app = FastAPI(
    title="LogiFlow",
    openapi_url="/openapi.json" if settings.DEBUG else None,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

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
