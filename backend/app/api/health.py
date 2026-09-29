import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", tags=["system"])
async def health_check(session: AsyncSession = Depends(get_db)):
    try:
        async with asyncio.timeout(2):
            await session.execute(text("SELECT 1"))
    except (SQLAlchemyError, TimeoutError) as exc:
        logger.exception("Readiness check failed: database is unavailable")
        raise HTTPException(
            status_code=503, detail="Database unavailable"
        ) from exc

    return {"status": "ok", "checks": {"database": "ok"}}
