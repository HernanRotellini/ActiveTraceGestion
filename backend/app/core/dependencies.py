"""Dependencias de FastAPI para inyección de recursos.

Implementadas en C-01:
  - get_db: sesión async de base de datos por request.

RESERVADOS (a llenar en changes posteriores):
  - get_current_user  → C-03 (auth JWT)
  - get_tenant        → C-02 (resolución de tenant)
  - require_permission → C-04 (RBAC)
"""

from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_sessionmaker
from app.services.auth import AuthService, CurrentUser, AuthenticationError

bearer_scheme = HTTPBearer(auto_error=False)


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


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> CurrentUser:
    """Resuelve usuario y tenant exclusivamente desde JWT verificado."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        return await AuthService(db).current_user_from_token(credentials.credentials)
    except AuthenticationError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated") from exc
