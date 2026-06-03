"""Punto de entrada de la aplicación FastAPI.

Bootstrap:
  - Creación de la app FastAPI
  - Lifespan: inicialización de engine DB + logging + OpenTelemetry
  - Registro de routers
  - Middleware global
"""

import logging
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import Settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Maneja el ciclo de vida de la aplicación.

    Startup:
      - Carga configuración
      - Configura logging JSON
      - Inicializa engine de base de datos
      - Configura OpenTelemetry

    Shutdown:
      - Cierra el pool de conexiones de la DB
    """
    # ── Startup ─────────────────────────────────────────────
    settings = Settings()  # type: ignore[call-arg]

    from app.core.logging import configure_json_logging  # noqa: PLC0415
    configure_json_logging()

    logger.info("Iniciando activia-trace...")

    from app.core.database import create_engine_from_url, dispose_engine  # noqa: PLC0415
    connect_args: dict[str, object] = {}
    if sys.platform == "win32":
        connect_args["ssl"] = False
    create_engine_from_url(settings.DATABASE_URL, connect_args=connect_args)
    logger.info("Engine de base de datos inicializado")

    from app.core.observability import setup_observability  # noqa: PLC0415
    setup_observability(settings, app)

    yield

    # ── Shutdown ────────────────────────────────────────────
    logger.info("Deteniendo activia-trace...")
    await dispose_engine()
    logger.info("Engine de base de datos liberado")


def create_app() -> FastAPI:
    """Factory de la aplicación FastAPI.

    Returns:
        Instancia configurada de FastAPI.
    """
    app = FastAPI(
        title="activia-trace",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Registrar routers
    from app.api.v1.routers.asignaciones import router as asignaciones_router  # noqa: PLC0415
    from app.api.v1.routers.auth import router as auth_router  # noqa: PLC0415
    from app.api.v1.routers.equipos import router as equipos_router  # noqa: PLC0415
    from app.api.v1.routers.estructura_academica import router as estructura_academica_router  # noqa: PLC0415
    from app.api.v1.routers.health import router as health_router  # noqa: PLC0415
    from app.api.v1.routers.rbac import router as rbac_router  # noqa: PLC0415
    from app.api.v1.routers.usuarios import router as usuarios_router  # noqa: PLC0415
    app.include_router(asignaciones_router)
    app.include_router(auth_router)
    app.include_router(equipos_router)
    app.include_router(estructura_academica_router)
    app.include_router(health_router)
    app.include_router(rbac_router)
    app.include_router(usuarios_router)

    return app


# Instancia global para ASGI server (uvicorn)
app = create_app()
