"""Endpoint de salud de la aplicación.

GET /health — reporta liveness de la app y readiness de la base de datos.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Health-check: liveness + readiness de base de datos.

    Siempre responde 200 (degradado si DB no responde, nunca crash).
    """
    db_status = "up"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001
        logger.warning("Health check: DB no responde: %s", exc)
        db_status = "down"

    return {
        "status": "ok",
        "database": db_status,
    }
