"""Servicio de autorización RBAC."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.rbac import PermissionResolver


class AuthorizationService:
    """Resuelve permisos efectivos de un usuario en su tenant."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def effective_permissions(self, role_codes: list[str], tenant_id: UUID) -> set[str]:
        resolver = PermissionResolver(self.session, tenant_id)
        return await resolver.efectivos(role_codes)
