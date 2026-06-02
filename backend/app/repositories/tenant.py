"""Repositories de tenants."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import Tenant


class TenantRepository:
    """Acceso a tenants raíz para resolución pre-sesión permitida."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_active_by_code(self, code: str) -> Tenant | None:
        result = await self.session.execute(
            select(Tenant).where(Tenant.code == code, Tenant.is_active.is_(True), Tenant.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()
