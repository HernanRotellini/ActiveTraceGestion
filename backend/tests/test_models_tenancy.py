"""Tests TDD para modelos base multi-tenant."""

import asyncio
from collections.abc import AsyncGenerator
from uuid import UUID

import pytest
from sqlalchemy import String, inspect, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TenantScopedMixin
from app.models.tenant import Tenant


class ScopedRecord(TenantScopedMixin, Base):
    """Modelo tenant-scoped mínimo usado solo por tests."""

    __tablename__ = "test_scoped_records"

    name: Mapped[str] = mapped_column(String(50), nullable=False)


@pytest.fixture
async def tenancy_schema(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    """Crea tablas reales necesarias para probar modelos ORM."""
    bind = await db_session.connection()
    tables = [ScopedRecord.__table__, Tenant.__table__]
    await bind.execute(
        text("DROP TABLE IF EXISTS test_repository_records, test_scoped_records, tenants CASCADE")
    )
    await bind.run_sync(
        lambda sync_conn: Base.metadata.create_all(sync_conn, tables=list(reversed(tables)))
    )
    yield
    await db_session.rollback()


@pytest.mark.asyncio
class TestTenantModel:
    """Contrato del tenant raíz global."""

    async def test_tenant_has_uuid_timestamps_soft_delete_and_no_tenant_id(
        self,
        db_session: AsyncSession,
        tenancy_schema: None,
    ) -> None:
        tenant = Tenant(name="Universidad Tecnologica Nacional", code="utn")

        db_session.add(tenant)
        await db_session.commit()
        await db_session.refresh(tenant)

        assert isinstance(tenant.id, UUID)
        assert tenant.created_at is not None
        assert tenant.updated_at is not None
        assert tenant.deleted_at is None
        assert "tenant_id" not in inspect(Tenant).columns


@pytest.mark.asyncio
class TestTenantScopedMixin:
    """Contrato de campos base para entidades tenant-scoped."""

    async def test_tenant_scoped_record_gets_base_fields(
        self,
        db_session: AsyncSession,
        tenancy_schema: None,
    ) -> None:
        tenant = Tenant(name="Tenant A", code="tenant-a")
        db_session.add(tenant)
        await db_session.flush()
        record = ScopedRecord(tenant_id=tenant.id, name="Record A")

        db_session.add(record)
        await db_session.commit()
        await db_session.refresh(record)

        assert isinstance(record.id, UUID)
        assert record.tenant_id == tenant.id
        assert record.created_at is not None
        assert record.updated_at is not None
        assert record.deleted_at is None

    async def test_timestamps_update_without_changing_created_at(
        self,
        db_session: AsyncSession,
        tenancy_schema: None,
    ) -> None:
        tenant = Tenant(name="Tenant A", code="tenant-a")
        db_session.add(tenant)
        await db_session.flush()
        record = ScopedRecord(tenant_id=tenant.id, name="Original")
        db_session.add(record)
        await db_session.commit()
        await db_session.refresh(record)
        created_at = record.created_at
        updated_at = record.updated_at

        await asyncio.sleep(0.01)
        record.name = "Updated"
        await db_session.commit()
        await db_session.refresh(record)

        assert record.created_at == created_at
        assert record.updated_at > updated_at
