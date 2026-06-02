"""Fixtures compartidos para todos los tests del backend."""

import asyncio
import os
import sys

# Windows: SelectorEventLoop en lugar de ProactorEventLoop para compatibilidad
# con asyncpg (SSL handshake falla con ProactorEventLoop).
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings
from app.core.database import (
    Base,
    create_engine_from_url,
    dispose_engine,
    get_sessionmaker,
)

# ── Event loop session-scoped ───────────────────────────────────


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Event loop compartido para toda la sesión de tests.

    Necesario en Windows para evitar 'Event loop is closed' entre tests.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


# ── Settings de test ────────────────────────────────────────────


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Settings de test sin leer .env del proyecto.

    Usa _env_file=None para evitar contaminación con el .env de desarrollo,
    y setea valores mínimos válidos en variables de entorno.
    """
    os.environ.setdefault(
        "DATABASE_URL",
        "postgresql+asyncpg://trace:trace@localhost:5432/trace_test",
    )
    os.environ.setdefault("SECRET_KEY", "a" * 32)
    os.environ.setdefault("ENCRYPTION_KEY", "b" * 32)
    return Settings(_env_file=None)  # type: ignore[call-arg]


# ── Engine y sesión de test (session-scoped) ────────────────────


@pytest.fixture
async def db_engine(test_settings: Settings) -> AsyncGenerator[None, None]:
    """Inicializa el engine de test fresco por cada test.

    Función-scoped para evitar problemas de event loop en Windows
    con asyncpg. Cada test crea su propio pool de conexiones.
    """
    create_engine_from_url(test_settings.DATABASE_URL, connect_args={"ssl": False})
    try:
        yield
    finally:
        await dispose_engine()


@pytest.fixture
async def db_session(db_engine: None) -> AsyncGenerator[Any, None]:
    """Provee una sesión async limpia por test."""
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()


# ── Cliente HTTP async para tests ───────────────────────────────


@pytest.fixture
async def async_client(db_engine: None) -> AsyncGenerator[AsyncClient, None]:
    """Cliente HTTP async contra la app FastAPI (ASGI transport).

    Requiere db_engine para que la dependencia get_db funcione.
    """
    from app.main import create_app  # noqa: PLC0415

    app = create_app()
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
