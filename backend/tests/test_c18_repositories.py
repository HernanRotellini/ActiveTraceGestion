"""Tests para C-18 Liquidaciones y Honorarios: repositories.

Strict TDD: RED -> GREEN -> TRIANGULATE -> REFACTOR.
"""

from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base


@pytest.fixture
async def c18_repo_schema(db_engine: None):
    """Creates a fresh schema for C-18 repository tests."""
    from app.models.estructura_academica import Carrera, Cohorte, Materia  # noqa: F401
    from app.models.liquidaciones import Factura, Liquidacion, MateriaPlus, SalarioBase, SalarioPlus  # noqa: F401
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
async def tenant_id(db_session: AsyncSession, c18_repo_schema: None) -> UUID:
    from app.models.tenant import Tenant

    tenant = Tenant(id=uuid4(), name="Tenant C18 Repo", code=f"c18repo-{uuid4().hex[:8]}")
    db_session.add(tenant)
    await db_session.flush()
    return tenant.id


@pytest.fixture
async def otro_tenant_id(db_session: AsyncSession, c18_repo_schema: None) -> UUID:
    from app.models.tenant import Tenant

    tenant = Tenant(id=uuid4(), name="Otro Tenant C18 Repo", code=f"c18repo-other-{uuid4().hex[:8]}")
    db_session.add(tenant)
    await db_session.flush()
    return tenant.id


async def crear_usuario(db_session: AsyncSession, tenant_id: UUID, **overrides) -> UUID:
    from app.models.usuarios_asignaciones import Usuario

    defaults = {
        "tenant_id": tenant_id,
        "nombre": "Docente",
        "apellidos": "Repo",
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

    defaults = {"tenant_id": tenant_id, "codigo": f"CAR-{uuid4().hex[:6]}", "nombre": "Carrera Repo"}
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

    defaults = {"tenant_id": tenant_id, "codigo": f"MAT-{uuid4().hex[:6]}", "nombre": "Materia Repo"}
    defaults.update(overrides)
    obj = Materia(**defaults)
    db_session.add(obj)
    await db_session.flush()
    return obj.id


class TestGrillaSalarialRepositories:
    async def test_salario_base_crud_lookup_vigente_y_active_only(
        self, db_session: AsyncSession, c18_repo_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.liquidaciones import RolLiquidacion
        from app.repositories.liquidacion_repository import SalarioBaseRepository

        repo = SalarioBaseRepository(db_session, tenant_id)
        vencido = await repo.create(
            rol=RolLiquidacion.PROFESOR,
            monto=Decimal("90000.00"),
            desde=date(2025, 1, 1),
            hasta=date(2025, 12, 31),
        )
        vigente = await repo.create(rol=RolLiquidacion.PROFESOR, monto=Decimal("120000.00"), desde=date(2026, 1, 1))
        await repo.soft_delete(vencido.id)
        await db_session.flush()

        assert await repo.get(vencido.id) is None
        assert [item.id for item in await repo.list()] == [vigente.id]

        found = await repo.get_vigente(rol=RolLiquidacion.PROFESOR, periodo=date(2026, 6, 1))
        assert found is not None
        assert found.id == vigente.id

        updated = await repo.update(vigente.id, monto=Decimal("125000.00"), hasta=date(2026, 12, 31))
        assert updated is not None
        assert updated.monto == Decimal("125000.00")
        assert updated.hasta == date(2026, 12, 31)

    async def test_salario_base_overlap_detection_cross_tenant_y_boundaries(
        self, db_session: AsyncSession, c18_repo_schema: None, tenant_id: UUID, otro_tenant_id: UUID
    ) -> None:
        from app.models.liquidaciones import RolLiquidacion
        from app.repositories.liquidacion_repository import SalarioBaseRepository

        repo = SalarioBaseRepository(db_session, tenant_id)
        otro_repo = SalarioBaseRepository(db_session, otro_tenant_id)
        existing = await repo.create(
            rol=RolLiquidacion.TUTOR,
            monto=Decimal("70000.00"),
            desde=date(2026, 1, 1),
            hasta=date(2026, 6, 30),
        )
        await otro_repo.create(
            rol=RolLiquidacion.TUTOR,
            monto=Decimal("1.00"),
            desde=date(2026, 7, 1),
            hasta=date(2026, 12, 31),
        )

        assert await repo.has_overlap(rol=RolLiquidacion.TUTOR, desde=date(2026, 6, 30), hasta=date(2026, 7, 31))
        assert not await repo.has_overlap(rol=RolLiquidacion.TUTOR, desde=date(2026, 7, 1), hasta=date(2026, 12, 31))
        assert not await repo.has_overlap(
            rol=RolLiquidacion.TUTOR,
            desde=date(2026, 1, 1),
            hasta=date(2026, 6, 30),
            exclude_id=existing.id,
        )

    async def test_vigencia_boundary_and_soft_deleted_overlap_are_not_active(
        self, db_session: AsyncSession, c18_repo_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.liquidaciones import RolLiquidacion
        from app.repositories.liquidacion_repository import SalarioBaseRepository

        repo = SalarioBaseRepository(db_session, tenant_id)
        ended = await repo.create(
            rol=RolLiquidacion.COORDINADOR,
            monto=Decimal("150000.00"),
            desde=date(2026, 1, 1),
            hasta=date(2026, 6, 30),
        )

        assert (await repo.get_vigente(rol=RolLiquidacion.COORDINADOR, periodo=date(2026, 6, 30))).id == ended.id
        assert await repo.get_vigente(rol=RolLiquidacion.COORDINADOR, periodo=date(2026, 7, 1)) is None

        await repo.soft_delete(ended.id)
        await db_session.flush()
        assert not await repo.has_overlap(
            rol=RolLiquidacion.COORDINADOR,
            desde=date(2026, 6, 1),
            hasta=date(2026, 6, 30),
        )

    async def test_salario_plus_y_materia_plus_lookup_overlap_y_tenant_scope(
        self, db_session: AsyncSession, c18_repo_schema: None, tenant_id: UUID, otro_tenant_id: UUID
    ) -> None:
        from app.models.liquidaciones import RolLiquidacion
        from app.repositories.liquidacion_repository import MateriaPlusRepository, SalarioPlusRepository

        materia_id = await crear_materia(db_session, tenant_id)
        otra_materia_id = await crear_materia(db_session, otro_tenant_id, codigo="MAT-OTRA")
        plus_repo = SalarioPlusRepository(db_session, tenant_id)
        mapping_repo = MateriaPlusRepository(db_session, tenant_id)
        otro_mapping_repo = MateriaPlusRepository(db_session, otro_tenant_id)

        plus = await plus_repo.create(
            rol=RolLiquidacion.PROFESOR,
            grupo="PROG",
            descripcion="Programacion",
            monto=Decimal("35000.00"),
            desde=date(2026, 1, 1),
        )
        mapping = await mapping_repo.create(materia_id=materia_id, grupo="PROG", desde=date(2026, 1, 1), hasta=date(2026, 6, 30))
        other_mapping = await otro_mapping_repo.create(materia_id=otra_materia_id, grupo="PROG", desde=date(2026, 1, 1))

        found_plus = await plus_repo.get_vigente(rol=RolLiquidacion.PROFESOR, grupo="PROG", periodo=date(2026, 1, 1))
        found_mapping = await mapping_repo.get_vigente(materia_id=materia_id, periodo=date(2026, 6, 30))

        assert found_plus is not None and found_plus.id == plus.id
        assert found_mapping is not None and found_mapping.id == mapping.id
        assert await mapping_repo.get(other_mapping.id) is None
        assert await plus_repo.has_overlap(
            rol=RolLiquidacion.PROFESOR,
            grupo="PROG",
            desde=date(2026, 12, 1),
            hasta=None,
        )
        assert await mapping_repo.has_overlap(materia_id=materia_id, desde=date(2026, 6, 30), hasta=date(2026, 7, 31))
        assert not await mapping_repo.has_overlap(materia_id=materia_id, desde=date(2026, 7, 1), hasta=None)


class TestLiquidacionRepository:
    async def test_create_snapshot_detail_filters_y_duplicate_close(
        self, db_session: AsyncSession, c18_repo_schema: None, tenant_id: UUID, otro_tenant_id: UUID
    ) -> None:
        from app.models.liquidaciones import RolLiquidacion
        from app.repositories.liquidacion_repository import LiquidacionRepository

        usuario_id = await crear_usuario(db_session, tenant_id)
        otro_usuario_id = await crear_usuario(db_session, otro_tenant_id, email="otro-liq@example.com")
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)
        otra_carrera_id = await crear_carrera(db_session, otro_tenant_id)
        otra_cohorte_id = await crear_cohorte(db_session, otro_tenant_id, otra_carrera_id)
        repo = LiquidacionRepository(db_session, tenant_id)
        otro_repo = LiquidacionRepository(db_session, otro_tenant_id)

        snapshot = await repo.create_snapshot(
            cohorte_id=cohorte_id,
            usuario_id=usuario_id,
            periodo="2026-06",
            rol=RolLiquidacion.NEXO,
            monto_base=Decimal("100000.00"),
            monto_plus=Decimal("20000.00"),
            monto_total=Decimal("120000.00"),
            comisiones=["COM-1", "COM-2"],
            es_nexo=True,
        )
        other_snapshot = await otro_repo.create_snapshot(
            cohorte_id=otra_cohorte_id,
            usuario_id=otro_usuario_id,
            periodo="2026-06",
            rol=RolLiquidacion.PROFESOR,
            monto_base=Decimal("999999.00"),
            monto_plus=Decimal("0.00"),
            monto_total=Decimal("999999.00"),
            comisiones=[],
        )

        assert await repo.exists_closed(cohorte_id=cohorte_id, periodo="2026-06")
        assert not await repo.exists_closed(cohorte_id=cohorte_id, periodo="2026-07")
        assert await repo.get(other_snapshot.id) is None
        assert [item.id for item in await repo.list_filtered(periodo="2026-06")] == [snapshot.id]
        assert [item.id for item in await repo.list_filtered(cohorte_id=cohorte_id)] == [snapshot.id]
        assert [item.id for item in await repo.list_filtered(usuario_id=usuario_id)] == [snapshot.id]

    async def test_liquidacion_active_only_excluye_soft_delete(
        self, db_session: AsyncSession, c18_repo_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.liquidaciones import RolLiquidacion
        from app.repositories.liquidacion_repository import LiquidacionRepository

        usuario_id = await crear_usuario(db_session, tenant_id)
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)
        repo = LiquidacionRepository(db_session, tenant_id)
        visible = await repo.create_snapshot(
            cohorte_id=cohorte_id,
            usuario_id=usuario_id,
            periodo="2026-06",
            rol=RolLiquidacion.PROFESOR,
            monto_base=Decimal("100000.00"),
            monto_plus=Decimal("0.00"),
            monto_total=Decimal("100000.00"),
            comisiones=[],
        )
        borrada = await repo.create_snapshot(
            cohorte_id=cohorte_id,
            usuario_id=await crear_usuario(db_session, tenant_id),
            periodo="2026-06",
            rol=RolLiquidacion.TUTOR,
            monto_base=Decimal("70000.00"),
            monto_plus=Decimal("0.00"),
            monto_total=Decimal("70000.00"),
            comisiones=[],
        )
        await repo.soft_delete(borrada.id)
        await db_session.flush()

        assert [item.id for item in await repo.list_filtered(periodo="2026-06")] == [visible.id]

    async def test_list_filtered_por_segmento_contable_prioriza_facturante_sobre_nexo(
        self, db_session: AsyncSession, c18_repo_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.liquidaciones import RolLiquidacion
        from app.repositories.liquidacion_repository import LiquidacionRepository

        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)
        repo = LiquidacionRepository(db_session, tenant_id)
        general = await repo.create_snapshot(
            cohorte_id=cohorte_id,
            usuario_id=await crear_usuario(db_session, tenant_id),
            periodo="2026-06",
            rol=RolLiquidacion.PROFESOR,
            monto_base=Decimal("100000.00"),
            monto_plus=Decimal("0.00"),
            monto_total=Decimal("100000.00"),
            comisiones=[],
        )
        nexo = await repo.create_snapshot(
            cohorte_id=cohorte_id,
            usuario_id=await crear_usuario(db_session, tenant_id),
            periodo="2026-06",
            rol=RolLiquidacion.NEXO,
            monto_base=Decimal("50000.00"),
            monto_plus=Decimal("0.00"),
            monto_total=Decimal("50000.00"),
            comisiones=[],
            es_nexo=True,
        )
        facturante = await repo.create_snapshot(
            cohorte_id=cohorte_id,
            usuario_id=await crear_usuario(db_session, tenant_id),
            periodo="2026-06",
            rol=RolLiquidacion.PROFESOR,
            monto_base=Decimal("100000.00"),
            monto_plus=Decimal("0.00"),
            monto_total=Decimal("100000.00"),
            comisiones=[],
            excluido_por_factura=True,
        )
        nexo_facturante = await repo.create_snapshot(
            cohorte_id=cohorte_id,
            usuario_id=await crear_usuario(db_session, tenant_id),
            periodo="2026-06",
            rol=RolLiquidacion.NEXO,
            monto_base=Decimal("50000.00"),
            monto_plus=Decimal("0.00"),
            monto_total=Decimal("50000.00"),
            comisiones=[],
            es_nexo=True,
            excluido_por_factura=True,
        )

        assert [item.id for item in await repo.list_filtered(segmento="general")] == [general.id]
        assert [item.id for item in await repo.list_filtered(segmento="nexo")] == [nexo.id]
        assert {item.id for item in await repo.list_filtered(segmento="facturante")} == {facturante.id, nexo_facturante.id}


class TestFacturaRepository:
    async def test_factura_crud_update_mark_abonada_y_soft_delete(
        self, db_session: AsyncSession, c18_repo_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.liquidaciones import EstadoFactura
        from app.repositories.liquidacion_repository import FacturaRepository

        usuario_id = await crear_usuario(db_session, tenant_id, facturador=True)
        repo = FacturaRepository(db_session, tenant_id)
        factura = await repo.create(
            usuario_id=usuario_id,
            periodo="2026-06",
            detalle="Factura docente",
            referencia_archivo="opaque-ref",
            archivo_size_bytes=2048,
        )

        updated = await repo.update(factura.id, detalle="Factura actualizada", referencia_archivo="opaque-new")
        abonada = await repo.mark_abonada(factura.id, abonada_at=datetime(2026, 6, 30, tzinfo=UTC))

        assert updated is not None and updated.detalle == "Factura actualizada"
        assert updated.referencia_archivo == "opaque-new"
        assert abonada is not None
        assert abonada.estado == EstadoFactura.ABONADA
        assert abonada.abonada_at == datetime(2026, 6, 30, tzinfo=UTC)
        assert await repo.soft_delete(factura.id) is True
        await db_session.flush()
        assert await repo.get(factura.id) is None

    async def test_factura_filters_usuario_periodo_estado_date_range_y_cross_tenant(
        self, db_session: AsyncSession, c18_repo_schema: None, tenant_id: UUID, otro_tenant_id: UUID
    ) -> None:
        from app.models.liquidaciones import EstadoFactura
        from app.repositories.liquidacion_repository import FacturaRepository

        usuario_id = await crear_usuario(db_session, tenant_id, facturador=True)
        otro_usuario_id = await crear_usuario(db_session, otro_tenant_id, email="otro-factura@example.com", facturador=True)
        repo = FacturaRepository(db_session, tenant_id)
        otro_repo = FacturaRepository(db_session, otro_tenant_id)
        pendiente = await repo.create(
            usuario_id=usuario_id,
            periodo="2026-06",
            detalle="Pendiente junio",
            referencia_archivo="ref-1",
            archivo_size_bytes=100,
        )
        abonada = await repo.create(
            usuario_id=usuario_id,
            periodo="2026-07",
            detalle="Abonada julio",
            referencia_archivo="ref-2",
            archivo_size_bytes=200,
        )
        other = await otro_repo.create(
            usuario_id=otro_usuario_id,
            periodo="2026-06",
            detalle="Cross tenant",
            referencia_archivo="ref-otro",
            archivo_size_bytes=300,
        )
        pendiente.created_at = datetime(2026, 6, 10, tzinfo=UTC)
        abonada.created_at = datetime(2026, 7, 10, tzinfo=UTC)
        await repo.mark_abonada(abonada.id, abonada_at=datetime(2026, 7, 31, tzinfo=UTC))
        await db_session.flush()

        assert [item.id for item in await repo.list_filtered(usuario_id=usuario_id)] == [pendiente.id, abonada.id]
        assert [item.id for item in await repo.list_filtered(periodo="2026-06", estado=EstadoFactura.PENDIENTE)] == [pendiente.id]
        assert [item.id for item in await repo.list_filtered(desde=date(2026, 6, 1), hasta=date(2026, 6, 30))] == [pendiente.id]
        assert await repo.get(other.id) is None
