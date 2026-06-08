"""Tests para C-18 Liquidaciones y Honorarios: servicios.

Strict TDD: RED -> GREEN -> TRIANGULATE -> REFACTOR.
"""

from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base


@pytest.fixture
async def c18_service_schema(db_engine: None):
    """Creates a fresh schema for C-18 service tests."""
    from app.models.audit_log import AuditLog  # noqa: F401
    from app.models.auth import AuthUser  # noqa: F401
    from app.models.estructura_academica import Carrera, Cohorte, Materia  # noqa: F401
    from app.models.liquidaciones import Factura, Liquidacion, MateriaPlus, SalarioBase, SalarioPlus  # noqa: F401
    from app.models.rbac import Permiso, Rol, RolPermiso  # noqa: F401
    from app.models.tenant import Tenant  # noqa: F401
    from app.models.usuarios_asignaciones import Asignacion, Usuario  # noqa: F401

    from app.core.database import get_sessionmaker

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        connection = await session.connection()
        await connection.execute(text("DROP SCHEMA public CASCADE"))
        await connection.execute(text("CREATE SCHEMA public"))
        await connection.run_sync(Base.metadata.create_all)
        await session.commit()


@pytest.fixture
async def tenant_id(db_session: AsyncSession, c18_service_schema: None) -> UUID:
    from app.models.tenant import Tenant

    tenant = Tenant(id=uuid4(), name="Tenant C18 Service", code=f"c18svc-{uuid4().hex[:8]}")
    db_session.add(tenant)
    await db_session.flush()
    return tenant.id


@pytest.fixture
async def otro_tenant_id(db_session: AsyncSession, c18_service_schema: None) -> UUID:
    from app.models.tenant import Tenant

    tenant = Tenant(id=uuid4(), name="Otro Tenant C18 Service", code=f"c18svc-other-{uuid4().hex[:8]}")
    db_session.add(tenant)
    await db_session.flush()
    return tenant.id


async def crear_auth_user(db_session: AsyncSession, tenant_id: UUID) -> UUID:
    from app.models.auth import AuthUser

    user = AuthUser(
        tenant_id=tenant_id,
        email=f"finanzas-{uuid4().hex[:8]}@example.com",
        password_hash="hash",
        roles=["FINANZAS"],
    )
    db_session.add(user)
    await db_session.flush()
    return user.id


async def crear_usuario(db_session: AsyncSession, tenant_id: UUID, **overrides) -> UUID:
    from app.models.usuarios_asignaciones import Usuario

    defaults = {
        "tenant_id": tenant_id,
        "nombre": "Docente",
        "apellidos": "Servicio",
        "email": f"docente-{uuid4().hex[:8]}@example.com",
        "facturador": False,
        "banco": "Banco Test",
        "cbu": "encrypted-cbu",
    }
    defaults.update(overrides)
    obj = Usuario(**defaults)
    db_session.add(obj)
    await db_session.flush()
    return obj.id


async def crear_carrera(db_session: AsyncSession, tenant_id: UUID) -> UUID:
    from app.models.estructura_academica import Carrera

    obj = Carrera(tenant_id=tenant_id, codigo=f"CAR-{uuid4().hex[:6]}", nombre="Carrera Servicio")
    db_session.add(obj)
    await db_session.flush()
    return obj.id


async def crear_cohorte(db_session: AsyncSession, tenant_id: UUID, carrera_id: UUID) -> UUID:
    from app.models.estructura_academica import Cohorte

    obj = Cohorte(tenant_id=tenant_id, carrera_id=carrera_id, nombre=f"Coh-{uuid4().hex[:4]}", anio=2026, vig_desde=date(2026, 1, 1))
    db_session.add(obj)
    await db_session.flush()
    return obj.id


async def crear_materia(db_session: AsyncSession, tenant_id: UUID, **overrides) -> UUID:
    from app.models.estructura_academica import Materia

    defaults = {"tenant_id": tenant_id, "codigo": f"MAT-{uuid4().hex[:6]}", "nombre": "Materia Servicio"}
    defaults.update(overrides)
    obj = Materia(**defaults)
    db_session.add(obj)
    await db_session.flush()
    return obj.id


async def crear_asignacion(
    db_session: AsyncSession,
    tenant_id: UUID,
    *,
    usuario_id: UUID,
    cohorte_id: UUID,
    rol: str,
    materia_id: UUID | None = None,
    comisiones: list[str] | None = None,
) -> UUID:
    from app.models.usuarios_asignaciones import Asignacion

    obj = Asignacion(
        tenant_id=tenant_id,
        usuario_id=usuario_id,
        rol=rol,
        materia_id=materia_id,
        cohorte_id=cohorte_id,
        comisiones=comisiones or [],
        desde=date(2026, 1, 1),
    )
    db_session.add(obj)
    await db_session.flush()
    return obj.id


class TestGrillaSalarialService:
    async def test_crea_base_valida_y_rechaza_solapamiento(
        self, db_session: AsyncSession, tenant_id: UUID, c18_service_schema: None
    ) -> None:
        from app.models.liquidaciones import RolLiquidacion
        from app.services.grilla_salarial_service import GrillaSalarialOverlapError, GrillaSalarialService

        service = GrillaSalarialService(db_session, tenant_id)
        created = await service.create_salario_base(
            rol=RolLiquidacion.PROFESOR,
            monto=Decimal("120000.00"),
            desde=date(2026, 1, 1),
            hasta=date(2026, 6, 30),
        )

        assert created.tenant_id == tenant_id
        with pytest.raises(GrillaSalarialOverlapError):
            await service.create_salario_base(
                rol=RolLiquidacion.PROFESOR,
                monto=Decimal("130000.00"),
                desde=date(2026, 6, 30),
                hasta=date(2026, 12, 31),
            )

    async def test_rechaza_vigencia_invalida_y_materia_plus_cross_tenant(
        self, db_session: AsyncSession, tenant_id: UUID, otro_tenant_id: UUID, c18_service_schema: None
    ) -> None:
        from app.services.grilla_salarial_service import GrillaSalarialContextError, GrillaSalarialValidationError, GrillaSalarialService

        materia_otro_tenant = await crear_materia(db_session, otro_tenant_id)
        service = GrillaSalarialService(db_session, tenant_id)

        with pytest.raises(GrillaSalarialValidationError):
            await service.create_materia_plus(
                materia_id=materia_otro_tenant,
                grupo="PROG",
                desde=date(2026, 7, 1),
                hasta=date(2026, 6, 30),
            )
        with pytest.raises(GrillaSalarialContextError):
            await service.create_materia_plus(materia_id=materia_otro_tenant, grupo="PROG", desde=date(2026, 1, 1))


class TestLiquidacionServicePreview:
    async def test_preview_calcula_base_plus_por_comision_y_materia_sin_plus(
        self, db_session: AsyncSession, tenant_id: UUID, c18_service_schema: None
    ) -> None:
        from app.models.liquidaciones import RolLiquidacion
        from app.services.grilla_salarial_service import GrillaSalarialService
        from app.services.liquidacion_service import LiquidacionService

        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)
        materia_con_plus = await crear_materia(db_session, tenant_id, codigo="PROG-1")
        materia_sin_plus = await crear_materia(db_session, tenant_id, codigo="HIST-1")
        docente_id = await crear_usuario(db_session, tenant_id)
        await crear_asignacion(
            db_session,
            tenant_id,
            usuario_id=docente_id,
            cohorte_id=cohorte_id,
            rol="PROFESOR",
            materia_id=materia_con_plus,
            comisiones=["A", "B", "C"],
        )
        await crear_asignacion(
            db_session,
            tenant_id,
            usuario_id=docente_id,
            cohorte_id=cohorte_id,
            rol="PROFESOR",
            materia_id=materia_sin_plus,
            comisiones=["D"],
        )
        grilla = GrillaSalarialService(db_session, tenant_id)
        await grilla.create_salario_base(rol=RolLiquidacion.PROFESOR, monto=Decimal("100000.00"), desde=date(2026, 1, 1))
        await grilla.create_salario_plus(
            rol=RolLiquidacion.PROFESOR,
            grupo="PROG",
            descripcion="Programacion",
            monto=Decimal("10000.00"),
            desde=date(2026, 1, 1),
        )
        await grilla.create_materia_plus(materia_id=materia_con_plus, grupo="PROG", desde=date(2026, 1, 1))

        preview = await LiquidacionService(db_session, tenant_id).preview(cohorte_id=cohorte_id, periodo="2026-06")

        assert len(preview.items) == 1
        assert preview.items[0].usuario_id == docente_id
        assert preview.items[0].monto_base == Decimal("100000.00")
        assert preview.items[0].monto_plus == Decimal("30000.00")
        assert preview.items[0].monto_total == Decimal("130000.00")
        assert preview.items[0].comisiones == ["A", "B", "C", "D"]
        assert preview.total_pagable == Decimal("130000.00")

    async def test_preview_segmenta_nexo_excluye_facturante_y_detecta_datos_bancarios(
        self, db_session: AsyncSession, tenant_id: UUID, c18_service_schema: None
    ) -> None:
        from app.models.liquidaciones import RolLiquidacion
        from app.services.grilla_salarial_service import GrillaSalarialService
        from app.services.liquidacion_service import LiquidacionService

        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)
        materia_id = await crear_materia(db_session, tenant_id)
        nexo_id = await crear_usuario(db_session, tenant_id)
        facturante_id = await crear_usuario(db_session, tenant_id, facturador=True)
        sin_banco_id = await crear_usuario(db_session, tenant_id, banco=None, cbu=None)
        await crear_asignacion(db_session, tenant_id, usuario_id=nexo_id, cohorte_id=cohorte_id, rol="NEXO", materia_id=materia_id, comisiones=["N1"])
        await crear_asignacion(db_session, tenant_id, usuario_id=facturante_id, cohorte_id=cohorte_id, rol="PROFESOR", materia_id=materia_id, comisiones=["F1"])
        await crear_asignacion(db_session, tenant_id, usuario_id=sin_banco_id, cohorte_id=cohorte_id, rol="TUTOR", materia_id=materia_id, comisiones=["T1"])
        grilla = GrillaSalarialService(db_session, tenant_id)
        await grilla.create_salario_base(rol=RolLiquidacion.NEXO, monto=Decimal("50000.00"), desde=date(2026, 1, 1))
        await grilla.create_salario_base(rol=RolLiquidacion.PROFESOR, monto=Decimal("100000.00"), desde=date(2026, 1, 1))
        await grilla.create_salario_base(rol=RolLiquidacion.TUTOR, monto=Decimal("70000.00"), desde=date(2026, 1, 1))

        preview = await LiquidacionService(db_session, tenant_id).preview(cohorte_id=cohorte_id, periodo="2026-06")

        by_user = {item.usuario_id: item for item in preview.items}
        assert by_user[nexo_id].es_nexo is True
        assert by_user[facturante_id].excluido_por_factura is True
        assert by_user[sin_banco_id].procesable is False
        assert by_user[sin_banco_id].motivo_no_procesable == "datos_bancarios_incompletos"
        assert preview.segmento_nexo_total == Decimal("50000.00")
        assert preview.segmento_facturantes_total == Decimal("100000.00")
        assert preview.total_pagable == Decimal("50000.00")

    async def test_preview_rechaza_base_o_plus_vigente_faltante(
        self, db_session: AsyncSession, tenant_id: UUID, c18_service_schema: None
    ) -> None:
        from app.models.liquidaciones import RolLiquidacion
        from app.services.grilla_salarial_service import GrillaSalarialService
        from app.services.liquidacion_service import LiquidacionMissingConfigurationError, LiquidacionService

        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)
        materia_id = await crear_materia(db_session, tenant_id)
        docente_id = await crear_usuario(db_session, tenant_id)
        await crear_asignacion(db_session, tenant_id, usuario_id=docente_id, cohorte_id=cohorte_id, rol="PROFESOR", materia_id=materia_id, comisiones=["A"])

        service = LiquidacionService(db_session, tenant_id)
        with pytest.raises(LiquidacionMissingConfigurationError):
            await service.preview(cohorte_id=cohorte_id, periodo="2026-06")

        grilla = GrillaSalarialService(db_session, tenant_id)
        await grilla.create_salario_base(rol=RolLiquidacion.PROFESOR, monto=Decimal("100000.00"), desde=date(2026, 1, 1))
        await grilla.create_materia_plus(materia_id=materia_id, grupo="PROG", desde=date(2026, 1, 1))
        with pytest.raises(LiquidacionMissingConfigurationError):
            await service.preview(cohorte_id=cohorte_id, periodo="2026-06")

    async def test_preview_comisiones_vacias_cuentan_como_una_comision_activa(
        self, db_session: AsyncSession, tenant_id: UUID, c18_service_schema: None
    ) -> None:
        from app.models.liquidaciones import RolLiquidacion
        from app.services.grilla_salarial_service import GrillaSalarialService
        from app.services.liquidacion_service import LiquidacionService

        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)
        materia_id = await crear_materia(db_session, tenant_id)
        docente_id = await crear_usuario(db_session, tenant_id)
        await crear_asignacion(
            db_session,
            tenant_id,
            usuario_id=docente_id,
            cohorte_id=cohorte_id,
            rol="COORDINADOR",
            materia_id=materia_id,
            comisiones=[],
        )
        grilla = GrillaSalarialService(db_session, tenant_id)
        await grilla.create_salario_base(rol=RolLiquidacion.COORDINADOR, monto=Decimal("100000.00"), desde=date(2026, 1, 1))
        await grilla.create_salario_plus(
            rol=RolLiquidacion.COORDINADOR,
            grupo="PROG",
            descripcion="Programacion",
            monto=Decimal("10000.00"),
            desde=date(2026, 1, 1),
        )
        await grilla.create_materia_plus(materia_id=materia_id, grupo="PROG", desde=date(2026, 1, 1))

        preview = await LiquidacionService(db_session, tenant_id).preview(cohorte_id=cohorte_id, periodo="2026-06")

        assert preview.items[0].monto_plus == Decimal("10000.00")
        assert preview.items[0].monto_total == Decimal("110000.00")


class TestLiquidacionServiceClose:
    async def test_close_persiste_snapshot_inmutable_rechaza_duplicado_y_audita(
        self, db_session: AsyncSession, tenant_id: UUID, c18_service_schema: None
    ) -> None:
        from app.models.audit_log import AuditLog
        from app.models.liquidaciones import RolLiquidacion
        from app.services.grilla_salarial_service import GrillaSalarialService
        from app.services.liquidacion_service import LiquidacionAlreadyClosedError, LiquidacionService

        actor_id = await crear_auth_user(db_session, tenant_id)
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)
        materia_id = await crear_materia(db_session, tenant_id)
        docente_id = await crear_usuario(db_session, tenant_id)
        await crear_asignacion(db_session, tenant_id, usuario_id=docente_id, cohorte_id=cohorte_id, rol="PROFESOR", materia_id=materia_id, comisiones=["A", "B"])
        grilla = GrillaSalarialService(db_session, tenant_id)
        await grilla.create_salario_base(rol=RolLiquidacion.PROFESOR, monto=Decimal("100000.00"), desde=date(2026, 1, 1), hasta=date(2026, 6, 30))
        await grilla.create_salario_plus(rol=RolLiquidacion.PROFESOR, grupo="PROG", descripcion="Programacion", monto=Decimal("10000.00"), desde=date(2026, 1, 1), hasta=date(2026, 6, 30))
        await grilla.create_materia_plus(materia_id=materia_id, grupo="PROG", desde=date(2026, 1, 1), hasta=date(2026, 6, 30))

        service = LiquidacionService(db_session, tenant_id)
        closed = await service.close(cohorte_id=cohorte_id, periodo="2026-06", actor_id=actor_id)
        await grilla.create_salario_base(rol=RolLiquidacion.PROFESOR, monto=Decimal("999999.00"), desde=date(2026, 7, 1))

        assert len(closed) == 1
        assert closed[0].monto_total == Decimal("120000.00")
        assert closed[0].comisiones == ["A", "B"]
        with pytest.raises(LiquidacionAlreadyClosedError):
            await service.close(cohorte_id=cohorte_id, periodo="2026-06", actor_id=actor_id)
        audit = (await db_session.execute(select(AuditLog).where(AuditLog.tenant_id == tenant_id))).scalar_one()
        assert audit.accion == "LIQUIDACION_CERRAR"
        assert audit.detalle["periodo"] == "2026-06"
        assert audit.filas_afectadas == 1

    async def test_list_closed_pasa_segmento_al_repositorio(self, db_session: AsyncSession, tenant_id: UUID, c18_service_schema: None) -> None:
        from app.services.liquidacion_service import LiquidacionService

        calls = []
        service = LiquidacionService(db_session, tenant_id)

        async def fake_list_filtered(**kwargs):
            calls.append(kwargs)
            return [type("LiquidacionStub", (), {"excluido_por_factura": False, "es_nexo": True})()]

        service._liquidacion_repo.list_filtered = fake_list_filtered

        records = await service.list_closed(periodo="2026-06", segmento="nexo")

        assert calls == [{"periodo": "2026-06", "cohorte_id": None, "usuario_id": None, "segmento": "nexo"}]
        assert records[0].es_nexo is True
        assert records[0].excluido_por_factura is False


class TestFacturaService:
    async def test_registra_factura_solo_facturante_y_referencia_opaca(
        self, db_session: AsyncSession, tenant_id: UUID, c18_service_schema: None
    ) -> None:
        from app.models.liquidaciones import EstadoFactura
        from app.services.factura_service import FacturaService, FacturaUsuarioNoFacturanteError

        facturante_id = await crear_usuario(db_session, tenant_id, facturador=True)
        no_facturante_id = await crear_usuario(db_session, tenant_id, facturador=False)
        service = FacturaService(db_session, tenant_id)
        factura = await service.register_factura(
            usuario_id=facturante_id,
            periodo="2026-06",
            detalle="Factura junio",
            referencia_archivo="opaque://facturas/docente-1",
            archivo_size_bytes=2048,
        )

        assert factura.estado == EstadoFactura.PENDIENTE
        assert factura.referencia_archivo == "opaque://facturas/docente-1"
        with pytest.raises(FacturaUsuarioNoFacturanteError):
            await service.register_factura(
                usuario_id=no_facturante_id,
                periodo="2026-06",
                detalle="No corresponde",
                referencia_archivo="opaque-ref",
                archivo_size_bytes=10,
            )

    async def test_pendiente_a_abonada_y_transiciones_invalidas(
        self, db_session: AsyncSession, tenant_id: UUID, c18_service_schema: None
    ) -> None:
        from app.models.liquidaciones import EstadoFactura
        from app.services.factura_service import FacturaInvalidTransitionError, FacturaService

        facturante_id = await crear_usuario(db_session, tenant_id, facturador=True)
        service = FacturaService(db_session, tenant_id)
        factura = await service.register_factura(
            usuario_id=facturante_id,
            periodo="2026-06",
            detalle="Factura junio",
            referencia_archivo="opaque-ref",
            archivo_size_bytes=2048,
        )

        abonada = await service.mark_abonada(factura.id, abonada_at=datetime(2026, 6, 30, tzinfo=UTC))

        assert abonada.estado == EstadoFactura.ABONADA
        assert abonada.abonada_at == datetime(2026, 6, 30, tzinfo=UTC)
        with pytest.raises(FacturaInvalidTransitionError):
            await service.mark_abonada(factura.id, abonada_at=datetime(2026, 7, 1, tzinfo=UTC))
