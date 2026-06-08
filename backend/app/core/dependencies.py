"""Dependencias de FastAPI para inyección de recursos.

Implementadas en C-01:
  - get_db: sesión async de base de datos por request.
  - require_permission: guard RBAC class-based.
"""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_sessionmaker
from app.services.auth import AuthService, CurrentUser, AuthenticationError
from app.services.authorization import AuthorizationService

bearer_scheme = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency que provee una sesión async por request.

    Abre una sesión, la yield (inyectada en el handler), y realiza
    commit/rollback automático al finalizar:

    - Si el handler lanza excepción → rollback y cierre
    - Si el handler retorna exitosamente → commit y cierre
    """
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
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


class RequirePermission:
    """FastAPI dependency parametrizada que verifica permiso del usuario autenticado.

    Uso:
        @router.get("/calificaciones")
        async def listar(_: Annotated[None, Depends(require_permission("calificaciones:importar"))]):
            ...
    """

    def __init__(self, permission: str) -> None:
        self.permission = permission

    async def __call__(
        self,
        current_user: CurrentUser = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> None:
        authz = AuthorizationService(db)
        effective = await authz.effective_permissions(current_user.roles, current_user.tenant_id)
        if self.permission not in effective:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: missing permission '{self.permission}'",
            )


def require_permission(permission: str) -> RequirePermission:
    """Shortcut para crear guard de permiso."""
    return RequirePermission(permission)


async def get_panel_auditoria_service(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> "PanelAuditoriaService":
    from app.services.panel_auditoria import PanelAuditoriaService  # noqa: PLC0415
    return PanelAuditoriaService(db=db, current_user=current_user)


async def get_audit_service(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Dependency que construye AuditService con IP/user-agent del request."""
    from app.services.audit import AuditService  # noqa: PLC0415

    ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "")
    return AuditService(db=db, current_user=current_user, ip=ip, user_agent=user_agent)


async def get_inbox_service(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> "InboxService":
    from app.services.inbox_service import InboxService  # noqa: PLC0415
    from app.core.config import Settings  # noqa: PLC0415
    settings = Settings()  # type: ignore[call-arg]
    return InboxService(db=db, tenant_id=current_user.tenant_id, encryption_key=settings.ENCRYPTION_KEY)

