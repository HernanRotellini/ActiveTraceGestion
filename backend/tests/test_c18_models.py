"""Tests para C-18 Liquidaciones y Honorarios: modelos y migracion.

Strict TDD: RED -> GREEN -> TRIANGULATE -> REFACTOR.
"""

from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base


@pytest.fixture
async def c18_schema(db_engine: None):
    """Creates a fresh schema for C-18 tests."""
    from app.models.estructura_academica import Carrera, Cohorte, Materia  # noqa: F401
    from app.models.liquidaciones import (  # noqa: F401
        EstadoFactura,
        EstadoLiquidacion,
        Factura,
        Liquidacion,
        MateriaPlus,
        RolLiquidacion,
        SalarioBase,
        SalarioPlus,
    )
    from app.models.rbac import Permiso, Rol, RolPermiso  # noqa: F401
    from app.models.tenant import Tenant  # noqa: F401
    from app.models.usuarios_asignaciones import Usuario  # noqa: F401

    from app.core.database import get_sessionmaker

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        connection = await session.connection()
        await connection.execute(text("DROP SCHEMA public CASCADE"))
        await connection.execute(text("CREATE SCHEMA public"))
        await connection.run_sync(Base.metadata.create_all)
        await session.commit()


@pytest.fixture
async def tenant_id(db_session: AsyncSession, c18_schema: None) -> UUID:
    from app.models.tenant import Tenant

    tenant = Tenant(id=uuid4(), name="Tenant C18", code=f"c18-{uuid4().hex[:8]}")
    db_session.add(tenant)
    await db_session.flush()
    return tenant.id


@pytest.fixture
async def otro_tenant_id(db_session: AsyncSession, c18_schema: None) -> UUID:
    from app.models.tenant import Tenant

    tenant = Tenant(id=uuid4(), name="Otro Tenant C18", code=f"c18-other-{uuid4().hex[:8]}")
    db_session.add(tenant)
    await db_session.flush()
    return tenant.id


async def crear_usuario(db_session: AsyncSession, tenant_id: UUID, **overrides) -> UUID:
    from app.models.usuarios_asignaciones import Usuario

    defaults = {
        "tenant_id": tenant_id,
        "nombre": "Docente",
        "apellidos": "Test",
        "email": f"docente-{uuid4().hex[:8]}@example.com",
        "facturador": False,
    }
    defaults.update(overrides)
    obj = Usuario(**defaults)
    db_session.add(obj)
    await db_session.flush()
    return obj.id


async def crear_carrera(db_session: AsyncSession, tenant_id: UUID, **overrides) -> UUID:
    from app.models.estructura_academica import Carrera

    defaults = {"tenant_id": tenant_id, "codigo": f"CAR-{uuid4().hex[:6]}", "nombre": "Carrera Test"}
    defaults.update(overrides)
    obj = Carrera(**defaults)
    db_session.add(obj)
    await db_session.flush()
    return obj.id


async def crear_cohorte(db_session: AsyncSession, tenant_id: UUID, carrera_id: UUID, **overrides) -> UUID:
    from app.models.estructura_academica import Cohorte

    defaults = {
        "tenant_id": tenant_id,
        "carrera_id": carrera_id,
        "nombre": f"Coh-{uuid4().hex[:4]}",
        "anio": 2026,
        "vig_desde": date(2026, 1, 1),
    }
    defaults.update(overrides)
    obj = Cohorte(**defaults)
    db_session.add(obj)
    await db_session.flush()
    return obj.id


async def crear_materia(db_session: AsyncSession, tenant_id: UUID, **overrides) -> UUID:
    from app.models.estructura_academica import Materia

    defaults = {"tenant_id": tenant_id, "codigo": f"MAT-{uuid4().hex[:6]}", "nombre": "Materia Test"}
    defaults.update(overrides)
    obj = Materia(**defaults)
    db_session.add(obj)
    await db_session.flush()
    return obj.id


class TestC18Enums:
    def test_enum_values(self) -> None:
        from app.models.liquidaciones import EstadoFactura, EstadoLiquidacion, RolLiquidacion

        assert [item.value for item in RolLiquidacion] == ["PROFESOR", "TUTOR", "NEXO", "COORDINADOR"]
        assert [item.value for item in EstadoLiquidacion] == ["Abierta", "Cerrada"]
        assert [item.value for item in EstadoFactura] == ["Pendiente", "Abonada"]


class TestGrillaSalarialModels:
    async def test_salario_base_persiste_campos_tenant_y_vigencia(
        self, db_session: AsyncSession, c18_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.liquidaciones import RolLiquidacion, SalarioBase

        salario = SalarioBase(
            tenant_id=tenant_id,
            rol=RolLiquidacion.PROFESOR,
            monto=Decimal("120000.50"),
            desde=date(2026, 1, 1),
            hasta=date(2026, 12, 31),
        )
        db_session.add(salario)
        await db_session.flush()

        assert salario.tenant_id == tenant_id
        assert salario.rol == RolLiquidacion.PROFESOR
        assert salario.monto == Decimal("120000.50")
        assert salario.desde == date(2026, 1, 1)
        assert salario.hasta == date(2026, 12, 31)
        assert salario.deleted_at is None

    async def test_salario_plus_persiste_grupo_descripcion_y_monto(
        self, db_session: AsyncSession, c18_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.liquidaciones import RolLiquidacion, SalarioPlus

        plus = SalarioPlus(
            tenant_id=tenant_id,
            rol=RolLiquidacion.PROFESOR,
            grupo="PROG",
            descripcion="Programacion",
            monto=Decimal("35000.00"),
            desde=date(2026, 1, 1),
        )
        db_session.add(plus)
        await db_session.flush()

        assert plus.grupo == "PROG"
        assert plus.descripcion == "Programacion"
        assert plus.monto == Decimal("35000.00")
        assert plus.hasta is None

    async def test_materia_plus_persiste_mapping_con_fk_materia(
        self, db_session: AsyncSession, c18_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.liquidaciones import MateriaPlus

        materia_id = await crear_materia(db_session, tenant_id, codigo="MAT-PROG")
        mapping = MateriaPlus(
            tenant_id=tenant_id,
            materia_id=materia_id,
            grupo="PROG",
            desde=date(2026, 1, 1),
        )
        db_session.add(mapping)
        await db_session.flush()

        assert mapping.tenant_id == tenant_id
        assert mapping.materia_id == materia_id
        assert mapping.grupo == "PROG"
        assert mapping.deleted_at is None

    async def test_salario_base_rechaza_duplicado_activo_mismo_tenant_rol_y_vigencia(
        self, db_session: AsyncSession, c18_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.liquidaciones import RolLiquidacion, SalarioBase

        original = SalarioBase(
            tenant_id=tenant_id,
            rol=RolLiquidacion.PROFESOR,
            monto=Decimal("100000.00"),
            desde=date(2026, 1, 1),
            hasta=date(2026, 6, 30),
        )
        db_session.add(original)
        await db_session.flush()

        duplicado = SalarioBase(
            tenant_id=tenant_id,
            rol=RolLiquidacion.PROFESOR,
            monto=Decimal("110000.00"),
            desde=date(2026, 1, 1),
            hasta=date(2026, 6, 30),
        )
        db_session.add(duplicado)
        with pytest.raises(IntegrityError):
            await db_session.flush()
        await db_session.rollback()

    async def test_salario_base_misma_vigencia_en_otro_tenant_ok(
        self, db_session: AsyncSession, c18_schema: None, tenant_id: UUID, otro_tenant_id: UUID
    ) -> None:
        from app.models.liquidaciones import RolLiquidacion, SalarioBase

        db_session.add_all(
            [
                SalarioBase(
                    tenant_id=tenant_id,
                    rol=RolLiquidacion.PROFESOR,
                    monto=Decimal("100000.00"),
                    desde=date(2026, 1, 1),
                    hasta=date(2026, 6, 30),
                ),
                SalarioBase(
                    tenant_id=otro_tenant_id,
                    rol=RolLiquidacion.PROFESOR,
                    monto=Decimal("100000.00"),
                    desde=date(2026, 1, 1),
                    hasta=date(2026, 6, 30),
                ),
            ]
        )
        await db_session.flush()

    async def test_soft_delete_permite_recrear_mapping_activo(
        self, db_session: AsyncSession, c18_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.liquidaciones import MateriaPlus

        materia_id = await crear_materia(db_session, tenant_id)
        anterior = MateriaPlus(
            tenant_id=tenant_id,
            materia_id=materia_id,
            grupo="PROG",
            desde=date(2026, 1, 1),
            hasta=date(2026, 12, 31),
        )
        db_session.add(anterior)
        await db_session.flush()
        anterior.deleted_at = datetime.now(UTC)
        await db_session.flush()

        nuevo = MateriaPlus(
            tenant_id=tenant_id,
            materia_id=materia_id,
            grupo="PROG",
            desde=date(2026, 1, 1),
            hasta=date(2026, 12, 31),
        )
        db_session.add(nuevo)
        await db_session.flush()
        assert nuevo.id != anterior.id


class TestLiquidacionModels:
    async def test_liquidacion_cerrada_persiste_snapshot(
        self, db_session: AsyncSession, c18_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.liquidaciones import EstadoLiquidacion, Liquidacion, RolLiquidacion

        usuario_id = await crear_usuario(db_session, tenant_id)
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)
        liquidacion = Liquidacion(
            tenant_id=tenant_id,
            cohorte_id=cohorte_id,
            usuario_id=usuario_id,
            periodo="2026-06",
            rol=RolLiquidacion.NEXO,
            estado=EstadoLiquidacion.CERRADA,
            monto_base=Decimal("100000.00"),
            monto_plus=Decimal("20000.00"),
            monto_total=Decimal("120000.00"),
            comisiones=["COM-1", "COM-2"],
            es_nexo=True,
            excluido_por_factura=False,
        )
        db_session.add(liquidacion)
        await db_session.flush()

        assert liquidacion.periodo == "2026-06"
        assert liquidacion.estado == EstadoLiquidacion.CERRADA
        assert liquidacion.monto_base == Decimal("100000.00")
        assert liquidacion.monto_plus == Decimal("20000.00")
        assert liquidacion.monto_total == Decimal("120000.00")
        assert liquidacion.comisiones == ["COM-1", "COM-2"]
        assert liquidacion.es_nexo is True

    async def test_liquidacion_cerrada_duplicada_rechazada_por_usuario_periodo_y_cohorte(
        self, db_session: AsyncSession, c18_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.liquidaciones import EstadoLiquidacion, Liquidacion, RolLiquidacion

        usuario_id = await crear_usuario(db_session, tenant_id)
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)
        original = Liquidacion(
            tenant_id=tenant_id,
            cohorte_id=cohorte_id,
            usuario_id=usuario_id,
            periodo="2026-06",
            rol=RolLiquidacion.PROFESOR,
            estado=EstadoLiquidacion.CERRADA,
            monto_base=Decimal("100000.00"),
            monto_plus=Decimal("0.00"),
            monto_total=Decimal("100000.00"),
            comisiones=[],
        )
        db_session.add(original)
        await db_session.flush()

        duplicada = Liquidacion(
            tenant_id=tenant_id,
            cohorte_id=cohorte_id,
            usuario_id=usuario_id,
            periodo="2026-06",
            rol=RolLiquidacion.PROFESOR,
            estado=EstadoLiquidacion.CERRADA,
            monto_base=Decimal("110000.00"),
            monto_plus=Decimal("0.00"),
            monto_total=Decimal("110000.00"),
            comisiones=[],
        )
        db_session.add(duplicada)
        with pytest.raises(IntegrityError):
            await db_session.flush()
        await db_session.rollback()

    async def test_liquidacion_cross_tenant_aislamiento_por_repository_base(
        self, db_session: AsyncSession, c18_schema: None, tenant_id: UUID, otro_tenant_id: UUID
    ) -> None:
        from app.models.liquidaciones import EstadoLiquidacion, Liquidacion, RolLiquidacion
        from app.repositories.base import TenantScopedRepository

        usuario_id = await crear_usuario(db_session, tenant_id, email="t1@example.com")
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)
        otro_usuario_id = await crear_usuario(db_session, otro_tenant_id, email="t2@example.com")
        otra_carrera_id = await crear_carrera(db_session, otro_tenant_id)
        otra_cohorte_id = await crear_cohorte(db_session, otro_tenant_id, otra_carrera_id)
        db_session.add_all(
            [
                Liquidacion(
                    tenant_id=tenant_id,
                    cohorte_id=cohorte_id,
                    usuario_id=usuario_id,
                    periodo="2026-06",
                    rol=RolLiquidacion.PROFESOR,
                    estado=EstadoLiquidacion.CERRADA,
                    monto_base=Decimal("100000.00"),
                    monto_plus=Decimal("0.00"),
                    monto_total=Decimal("100000.00"),
                    comisiones=[],
                ),
                Liquidacion(
                    tenant_id=otro_tenant_id,
                    cohorte_id=otra_cohorte_id,
                    usuario_id=otro_usuario_id,
                    periodo="2026-06",
                    rol=RolLiquidacion.PROFESOR,
                    estado=EstadoLiquidacion.CERRADA,
                    monto_base=Decimal("999999.00"),
                    monto_plus=Decimal("0.00"),
                    monto_total=Decimal("999999.00"),
                    comisiones=[],
                ),
            ]
        )
        await db_session.flush()

        repo = TenantScopedRepository(db_session, Liquidacion, tenant_id)
        active = await repo.list()
        assert len(active) == 1
        assert active[0].monto_total == Decimal("100000.00")


class TestFacturaModels:
    async def test_factura_persiste_estado_pendiente_por_defecto(
        self, db_session: AsyncSession, c18_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.liquidaciones import EstadoFactura, Factura

        usuario_id = await crear_usuario(db_session, tenant_id, facturador=True)
        factura = Factura(
            tenant_id=tenant_id,
            usuario_id=usuario_id,
            periodo="2026-06",
            detalle="Factura docente junio",
            referencia_archivo="opaque-ref-123",
            archivo_size_bytes=2048,
        )
        db_session.add(factura)
        await db_session.flush()

        assert factura.estado == EstadoFactura.PENDIENTE
        assert factura.referencia_archivo == "opaque-ref-123"
        assert factura.archivo_size_bytes == 2048
        assert factura.abonada_at is None

    async def test_factura_abonada_persiste_fecha_pago(
        self, db_session: AsyncSession, c18_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.liquidaciones import EstadoFactura, Factura

        usuario_id = await crear_usuario(db_session, tenant_id, facturador=True)
        abonada_at = datetime(2026, 6, 30, tzinfo=UTC)
        factura = Factura(
            tenant_id=tenant_id,
            usuario_id=usuario_id,
            periodo="2026-06",
            detalle="Factura abonada",
            referencia_archivo="opaque-ref-456",
            archivo_size_bytes=4096,
            estado=EstadoFactura.ABONADA,
            abonada_at=abonada_at,
        )
        db_session.add(factura)
        await db_session.flush()

        assert factura.estado == EstadoFactura.ABONADA
        assert factura.abonada_at == abonada_at

    async def test_factura_soft_delete_excluye_activos(
        self, db_session: AsyncSession, c18_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.liquidaciones import Factura
        from app.repositories.base import TenantScopedRepository

        usuario_id = await crear_usuario(db_session, tenant_id, facturador=True)
        f1 = Factura(
            tenant_id=tenant_id,
            usuario_id=usuario_id,
            periodo="2026-06",
            detalle="Visible",
            referencia_archivo="ref-visible",
            archivo_size_bytes=1024,
        )
        f2 = Factura(
            tenant_id=tenant_id,
            usuario_id=usuario_id,
            periodo="2026-07",
            detalle="Oculta",
            referencia_archivo="ref-oculta",
            archivo_size_bytes=1024,
        )
        db_session.add_all([f1, f2])
        await db_session.flush()

        repo = TenantScopedRepository(db_session, Factura, tenant_id)
        await repo.soft_delete(f2.id)
        await db_session.flush()

        active = await repo.list()
        assert [factura.id for factura in active] == [f1.id]


def test_c18_migration_declares_tables_enums_indexes() -> None:
    migration_path = Path(__file__).resolve().parents[1] / "alembic" / "versions" / "20260608_0014_c18_liquidaciones.py"

    content = migration_path.read_text()

    assert 'revision: str = "20260608_0014"' in content
    assert 'down_revision: str | None = "20260607_0014"' in content
    for table_name in ["salario_base", "salario_plus", "materia_plus", "liquidacion", "factura"]:
        assert f'"{table_name}"' in content
    for enum_name in ["rol_liquidacion", "estado_liquidacion", "estado_factura"]:
        assert enum_name in content
    for index_name in [
        "uq_salario_base_tenant_rol_vigencia_activo",
        "uq_salario_plus_tenant_rol_grupo_vigencia_activo",
        "uq_materia_plus_tenant_materia_vigencia_activo",
        "uq_liquidacion_cerrada_tenant_periodo_cohorte_usuario",
        "ix_factura_tenant_periodo_estado",
    ]:
        assert index_name in content
