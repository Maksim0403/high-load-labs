from fastapi import APIRouter

from app.api.health import router as health_router
from app.api.v1.routes import auth, dashboard, order, vehicle

api_router = APIRouter()

api_router.include_router(health_router)

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(
    dashboard.router, prefix="/dashboard", tags=["dashboard"]
)
api_router.include_router(order.router, prefix="/orders", tags=["orders"])
api_router.include_router(
    vehicle.router, prefix="/vehicles", tags=["vehicles"]
)
