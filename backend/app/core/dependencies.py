"""Dependencias de FastAPI para inyección de recursos.

Implementadas en C-01:
  - get_db: sesión async de base de datos por request.

RESERVADOS (a llenar en changes posteriores):
  - get_current_user  → C-03 (auth JWT)
  - get_tenant        → C-02 (resolución de tenant)
  - require_permission → C-04 (RBAC)
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_sessionmaker


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency que provee una sesión async por request.

    Abre una sesión, la yield (inyectada en el handler), y la cierra
    en finally incluso ante excepción (no fuga de conexiones al pool).
    """
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        try:
            yield session
        finally:
            await session.close()
