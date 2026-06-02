"""Repository base async con scope obligatorio por tenant."""

from datetime import UTC, datetime
from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import TenantScopedMixin

ModelT = TypeVar("ModelT", bound=TenantScopedMixin)


class TenantContextRequiredError(ValueError):
    """Error fail-closed cuando falta contexto de tenant."""


class TenantScopedRepository(Generic[ModelT]):
    """Repository para entidades tenant-scoped."""

    def __init__(self, session: AsyncSession, model: type[ModelT], tenant_id: UUID) -> None:
        if tenant_id is None:
            raise TenantContextRequiredError("tenant_id is required for tenant-scoped repositories")
        if not hasattr(model, "tenant_id"):
            raise TenantContextRequiredError("model must define tenant_id for tenant-scoped repositories")
        self.session = session
        self.model = model
        self.tenant_id = tenant_id

    async def list(self) -> list[ModelT]:
        """Lista registros visibles del tenant actual."""
        result = await self.session.execute(
            select(self.model).where(
                self.model.tenant_id == self.tenant_id,
                self.model.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def get(self, record_id: UUID) -> ModelT | None:
        """Obtiene un registro por id dentro del tenant actual."""
        result = await self.session.execute(
            select(self.model).where(
                self.model.id == record_id,
                self.model.tenant_id == self.tenant_id,
                self.model.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def soft_delete(self, record_id: UUID) -> bool:
        """Marca un registro como eliminado dentro del tenant actual."""
        record = await self.get(record_id)
        if record is None:
            return False
        record.deleted_at = datetime.now(UTC)
        return True
