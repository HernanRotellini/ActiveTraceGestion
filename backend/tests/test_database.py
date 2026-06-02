"""Tests de conexión a base de datos async.

Verifica que el engine async y las sesiones funcionan contra PostgreSQL real.
NO se mockea la DB: usa una base de test real (DATABASE_URL_TEST).
"""

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_sessionmaker


@pytest.mark.asyncio
class TestDatabaseConnection:
    """Smoke tests de conexión a base de datos."""

    async def test_select_one(self, db_session: AsyncSession) -> None:
        """Una sesión async ejecuta SELECT 1 y obtiene resultado."""
        result = await db_session.execute(text("SELECT 1"))
        value = result.scalar_one()
        assert value == 1

    async def test_multiple_queries(self, db_session: AsyncSession) -> None:
        """La misma sesión puede ejecutar múltiples queries."""
        for _ in range(3):
            result = await db_session.execute(text("SELECT 1"))
            assert result.scalar_one() == 1


@pytest.mark.asyncio
class TestDatabaseErrorHandling:
    """Manejo de errores en la conexión."""

    async def test_session_close_on_exception(self, db_engine: None) -> None:
        """La sesión se maneja correctamente ante una excepción.

        Verifica que, tras una excepción dentro del contexto de sesión,
        se puede cerrar la sesión y obtener una nueva para seguir operando.
        """
        sessionmaker = get_sessionmaker()

        # Simular un error dentro de una sesión
        async with sessionmaker() as session:
            with pytest.raises(Exception):
                await session.execute(text("SELECT * FROM nonexistent_table"))

            # Cerrar la sesión con error
            await session.rollback()
            await session.close()

        # Una sesión nueva funciona correctamente
        async with sessionmaker() as new_session:
            result = await new_session.execute(text("SELECT 1"))
            assert result.scalar_one() == 1
