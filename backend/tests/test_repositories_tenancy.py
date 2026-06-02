"""Tests TDD para repositories tenant-scoped."""

from collections.abc import AsyncGenerator
from uuid import uuid4

import pytest
from sqlalchemy import String, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import BaseModelMixin, TenantScopedMixin
from app.models.tenant import Tenant
from app.repositories.base import TenantContextRequiredError, TenantScopedRepository


class RepositoryRecord(TenantScopedMixin, Base):
    """Modelo tenant-scoped mínimo usado para tests de repository."""

    __tablename__ = "test_repository_records"

    name: Mapped[str] = mapped_column(String(50), nullable=False)


class GlobalRecord(BaseModelMixin, Base):
    """Modelo sin tenant_id usado para validar fail-closed."""

    __tablename__ = "test_global_records"

    name: Mapped[str] = mapped_column(String(50), nullable=False)


@pytest.fixture
async def repository_schema(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    """Crea tablas reales para probar queries repository sobre PostgreSQL."""
    bind = await db_session.connection()
    tables = [RepositoryRecord.__table__, Tenant.__table__]
    await bind.execute(
        text("DROP TABLE IF EXISTS test_repository_records, test_scoped_records, tenants CASCADE")
    )
    await bind.run_sync(
        lambda sync_conn: Base.metadata.create_all(sync_conn, tables=list(reversed(tables)))
    )
    yield
    await db_session.rollback()


@pytest.fixture
async def tenants_and_records(
    db_session: AsyncSession,
    repository_schema: None,
) -> tuple[Tenant, Tenant, RepositoryRecord, RepositoryRecord]:
    """Persiste dos tenants y un registro por tenant."""
    tenant_a = Tenant(name="Tenant A", code="tenant-a")
    tenant_b = Tenant(name="Tenant B", code="tenant-b")
    db_session.add_all([tenant_a, tenant_b])
    await db_session.flush()
    record_a = RepositoryRecord(tenant_id=tenant_a.id, name="Record A")
    record_b = RepositoryRecord(tenant_id=tenant_b.id, name="Record B")
    db_session.add_all([record_a, record_b])
    await db_session.commit()
    return tenant_a, tenant_b, record_a, record_b


@pytest.mark.asyncio
class TestTenantScopedRepositoryIsolation:
    """Repository filtra por tenant por defecto."""

    async def test_list_returns_only_current_tenant_records(
        self,
        db_session: AsyncSession,
        tenants_and_records: tuple[Tenant, Tenant, RepositoryRecord, RepositoryRecord],
    ) -> None:
        tenant_a, _, record_a, _ = tenants_and_records
        repository = TenantScopedRepository(db_session, RepositoryRecord, tenant_id=tenant_a.id)

        records = await repository.list()

        assert [record.id for record in records] == [record_a.id]

    async def test_get_treats_cross_tenant_record_as_not_found(
        self,
        db_session: AsyncSession,
        tenants_and_records: tuple[Tenant, Tenant, RepositoryRecord, RepositoryRecord],
    ) -> None:
        tenant_a, _, _, record_b = tenants_and_records
        repository = TenantScopedRepository(db_session, RepositoryRecord, tenant_id=tenant_a.id)

        record = await repository.get(record_b.id)

        assert record is None


@pytest.mark.asyncio
class TestTenantScopedRepositoryFailClosed:
    """Repository rechaza uso sin contexto tenant-scoped válido."""

    async def test_missing_tenant_id_is_rejected(self, db_session: AsyncSession) -> None:
        with pytest.raises(TenantContextRequiredError):
            TenantScopedRepository(db_session, RepositoryRecord, tenant_id=None)  # type: ignore[arg-type]

    async def test_model_without_tenant_id_is_rejected(self, db_session: AsyncSession) -> None:
        with pytest.raises(TenantContextRequiredError):
            TenantScopedRepository(db_session, GlobalRecord, tenant_id=uuid4())  # type: ignore[type-var]


@pytest.mark.asyncio
class TestTenantScopedRepositorySoftDelete:
    """Repository usa soft delete y oculta registros borrados."""

    async def test_soft_delete_marks_deleted_at(
        self,
        db_session: AsyncSession,
        tenants_and_records: tuple[Tenant, Tenant, RepositoryRecord, RepositoryRecord],
    ) -> None:
        tenant_a, _, record_a, _ = tenants_and_records
        repository = TenantScopedRepository(db_session, RepositoryRecord, tenant_id=tenant_a.id)

        await repository.soft_delete(record_a.id)
        await db_session.commit()
        await db_session.refresh(record_a)

        assert record_a.deleted_at is not None

    async def test_soft_deleted_record_is_hidden_by_get_and_list(
        self,
        db_session: AsyncSession,
        tenants_and_records: tuple[Tenant, Tenant, RepositoryRecord, RepositoryRecord],
    ) -> None:
        tenant_a, _, record_a, _ = tenants_and_records
        repository = TenantScopedRepository(db_session, RepositoryRecord, tenant_id=tenant_a.id)

        await repository.soft_delete(record_a.id)
        await db_session.commit()

        assert await repository.get(record_a.id) is None
        assert await repository.list() == []

    async def test_soft_delete_keeps_row_in_database(
        self,
        db_session: AsyncSession,
        tenants_and_records: tuple[Tenant, Tenant, RepositoryRecord, RepositoryRecord],
    ) -> None:
        tenant_a, _, record_a, _ = tenants_and_records
        repository = TenantScopedRepository(db_session, RepositoryRecord, tenant_id=tenant_a.id)

        await repository.soft_delete(record_a.id)
        await db_session.commit()

        persisted = await db_session.get(RepositoryRecord, record_a.id)
        assert persisted is not None

    async def test_soft_delete_does_not_affect_cross_tenant_record(
        self,
        db_session: AsyncSession,
        tenants_and_records: tuple[Tenant, Tenant, RepositoryRecord, RepositoryRecord],
    ) -> None:
        tenant_a, _, _, record_b = tenants_and_records
        repository = TenantScopedRepository(db_session, RepositoryRecord, tenant_id=tenant_a.id)

        deleted = await repository.soft_delete(record_b.id)
        await db_session.commit()
        await db_session.refresh(record_b)

        assert deleted is False
        assert record_b.deleted_at is None
