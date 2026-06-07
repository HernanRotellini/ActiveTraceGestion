"""Tests para C-17 services: ProgramaService, FechaAcademicaService.

Strict TDD: RED -> GREEN -> TRIANGULATE -> REFACTOR.
"""

from datetime import date
from uuid import UUID, uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base


@pytest.fixture
async def c17_schema(db_engine: None):
    """Creates a fresh schema for C-17 service tests."""
    from app.models.auth import AuthUser  # noqa: F401
    from app.models.estructura_academica import Carrera, Cohorte, Materia  # noqa: F401
    from app.models.programas import FechaAcademica, ProgramaMateria, TipoFechaAcademica  # noqa: F401
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
async def tenant_id(db_session: AsyncSession, c17_schema: None) -> UUID:
    from app.models.tenant import Tenant

    tenant = Tenant(id=uuid4(), name="Tenant C17 Svc", code=f"c17s-{uuid4().hex[:8]}")
    db_session.add(tenant)
    await db_session.flush()
    return tenant.id


@pytest.fixture
async def otro_tenant_id(db_session: AsyncSession, c17_schema: None) -> UUID:
    from app.models.tenant import Tenant

    tenant = Tenant(id=uuid4(), name="Otro Tenant C17 Svc", code=f"c17s-other-{uuid4().hex[:8]}")
    db_session.add(tenant)
    await db_session.flush()
    return tenant.id


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

    defaults = {"tenant_id": tenant_id, "carrera_id": carrera_id, "nombre": f"Coh-{uuid4().hex[:4]}", "anio": 2026, "vig_desde": date(2026, 1, 1)}
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


class TestProgramaMateriaService:
    async def test_create_programa_valido(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID
    ) -> None:
        from app.services.programa_service import ProgramaService

        materia_id = await crear_materia(db_session, tenant_id)
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)

        service = ProgramaService(db_session, tenant_id)
        programa = await service.create_programa(
            materia_id=materia_id,
            carrera_id=carrera_id,
            cohorte_id=cohorte_id,
            titulo="Programa Analítico 2026",
            referencia_archivo="/files/programa.pdf",
        )

        assert programa.titulo == "Programa Analítico 2026"
        assert programa.referencia_archivo == "/files/programa.pdf"
        assert programa.materia_id == materia_id
        assert programa.carrera_id == carrera_id
        assert programa.cohorte_id == cohorte_id
        assert programa.tenant_id == tenant_id
        assert programa.deleted_at is None

    async def test_create_programa_rechaza_contexto_cross_tenant(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID, otro_tenant_id: UUID
    ) -> None:
        from app.services.programa_service import ProgramaNotFoundError, ProgramaService

        materia_id = await crear_materia(db_session, otro_tenant_id, codigo="MAT-CROSS")
        carrera_id = await crear_carrera(db_session, otro_tenant_id, codigo="CAR-CROSS")
        cohorte_id = await crear_cohorte(db_session, otro_tenant_id, carrera_id, nombre="Coh-Cross")

        service = ProgramaService(db_session, tenant_id)
        with pytest.raises(ProgramaNotFoundError):
            await service.create_programa(
                materia_id=materia_id,
                carrera_id=carrera_id,
                cohorte_id=cohorte_id,
                titulo="Cross",
                referencia_archivo="/cross.pdf",
            )

    async def test_create_programa_rechaza_duplicado(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID
    ) -> None:
        from app.services.programa_service import ProgramaService, ProgramaValidationError

        materia_id = await crear_materia(db_session, tenant_id)
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)

        service = ProgramaService(db_session, tenant_id)
        await service.create_programa(
            materia_id=materia_id,
            carrera_id=carrera_id,
            cohorte_id=cohorte_id,
            titulo="Unico",
            referencia_archivo="/f.pdf",
        )

        with pytest.raises(ProgramaValidationError):
            await service.create_programa(
                materia_id=materia_id,
                carrera_id=carrera_id,
                cohorte_id=cohorte_id,
                titulo="Unico",
                referencia_archivo="/f2.pdf",
            )

    async def test_create_programa_rechaza_materia_inexistente(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID
    ) -> None:
        from app.services.programa_service import ProgramaNotFoundError, ProgramaService

        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)

        service = ProgramaService(db_session, tenant_id)
        with pytest.raises(ProgramaNotFoundError):
            await service.create_programa(
                materia_id=uuid4(),
                carrera_id=carrera_id,
                cohorte_id=cohorte_id,
                titulo="No Materia",
                referencia_archivo="/f.pdf",
            )

    async def test_create_programa_rechaza_carrera_inexistente(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID
    ) -> None:
        from app.services.programa_service import ProgramaNotFoundError, ProgramaService

        materia_id = await crear_materia(db_session, tenant_id)
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)

        service = ProgramaService(db_session, tenant_id)
        with pytest.raises(ProgramaNotFoundError):
            await service.create_programa(
                materia_id=materia_id,
                carrera_id=uuid4(),
                cohorte_id=cohorte_id,
                titulo="No Carrera",
                referencia_archivo="/f.pdf",
            )

    async def test_create_programa_rechaza_cohorte_inexistente(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID
    ) -> None:
        from app.services.programa_service import ProgramaNotFoundError, ProgramaService

        materia_id = await crear_materia(db_session, tenant_id)
        carrera_id = await crear_carrera(db_session, tenant_id)

        service = ProgramaService(db_session, tenant_id)
        with pytest.raises(ProgramaNotFoundError):
            await service.create_programa(
                materia_id=materia_id,
                carrera_id=carrera_id,
                cohorte_id=uuid4(),
                titulo="No Cohorte",
                referencia_archivo="/f.pdf",
            )

    async def test_list_programas(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID
    ) -> None:
        from app.services.programa_service import ProgramaService

        materia_id = await crear_materia(db_session, tenant_id)
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)

        service = ProgramaService(db_session, tenant_id)
        await service.create_programa(materia_id=materia_id, carrera_id=carrera_id, cohorte_id=cohorte_id, titulo="P1", referencia_archivo="/f1.pdf")
        await service.create_programa(materia_id=materia_id, carrera_id=carrera_id, cohorte_id=cohorte_id, titulo="P2", referencia_archivo="/f2.pdf")
        await service.create_programa(materia_id=materia_id, carrera_id=carrera_id, cohorte_id=cohorte_id, titulo="P3", referencia_archivo="/f3.pdf")

        all_items = await service.list_programas()
        assert len(all_items) == 3

    async def test_get_programa(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID
    ) -> None:
        from app.services.programa_service import ProgramaService

        materia_id = await crear_materia(db_session, tenant_id)
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)

        service = ProgramaService(db_session, tenant_id)
        created = await service.create_programa(materia_id=materia_id, carrera_id=carrera_id, cohorte_id=cohorte_id, titulo="Detail", referencia_archivo="/detail.pdf")

        fetched = await service.get_programa(created.id)
        assert fetched.id == created.id
        assert fetched.titulo == "Detail"

    async def test_update_programa(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID
    ) -> None:
        from app.services.programa_service import ProgramaService

        materia_id = await crear_materia(db_session, tenant_id)
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)

        service = ProgramaService(db_session, tenant_id)
        created = await service.create_programa(materia_id=materia_id, carrera_id=carrera_id, cohorte_id=cohorte_id, titulo="Original", referencia_archivo="/orig.pdf")

        updated = await service.update_programa(created.id, titulo="Updated", referencia_archivo="/new.pdf")
        assert updated.titulo == "Updated"
        assert updated.referencia_archivo == "/new.pdf"

    async def test_delete_programa_soft_delete(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID
    ) -> None:
        from app.services.programa_service import ProgramaService

        materia_id = await crear_materia(db_session, tenant_id)
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)

        service = ProgramaService(db_session, tenant_id)
        created = await service.create_programa(materia_id=materia_id, carrera_id=carrera_id, cohorte_id=cohorte_id, titulo="To Delete", referencia_archivo="/del.pdf")

        assert await service.get_programa(created.id) is not None
        await service.delete_programa(created.id)

        from app.services.programa_service import ProgramaNotFoundError
        with pytest.raises(ProgramaNotFoundError):
            await service.get_programa(created.id)


class TestFechaAcademicaService:
    async def test_create_fecha_valida(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.programas import TipoFechaAcademica
        from app.services.fecha_academica_service import FechaAcademicaService

        materia_id = await crear_materia(db_session, tenant_id)
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)

        service = FechaAcademicaService(db_session, tenant_id)
        fecha = await service.create_fecha(
            materia_id=materia_id,
            cohorte_id=cohorte_id,
            tipo=TipoFechaAcademica.PARCIAL,
            numero=1,
            periodo="2026-1C",
            fecha=date(2026, 5, 15),
            titulo="Primer Parcial",
        )

        assert fecha.titulo == "Primer Parcial"
        assert fecha.tipo == TipoFechaAcademica.PARCIAL
        assert fecha.numero == 1
        assert fecha.tenant_id == tenant_id

    async def test_create_fecha_rechaza_duplicado(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.programas import TipoFechaAcademica
        from app.services.fecha_academica_service import FechaAcademicaService, FechaValidationError

        materia_id = await crear_materia(db_session, tenant_id)
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)

        service = FechaAcademicaService(db_session, tenant_id)
        await service.create_fecha(materia_id=materia_id, cohorte_id=cohorte_id, tipo=TipoFechaAcademica.PARCIAL, numero=1, periodo="2026-1C", fecha=date(2026, 5, 15), titulo="Original")

        with pytest.raises(FechaValidationError):
            await service.create_fecha(materia_id=materia_id, cohorte_id=cohorte_id, tipo=TipoFechaAcademica.PARCIAL, numero=1, periodo="2026-1C", fecha=date(2026, 6, 1), titulo="Duplicado")

    async def test_create_fecha_mismo_contexto_diferente_tipo_ok(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.programas import TipoFechaAcademica
        from app.services.fecha_academica_service import FechaAcademicaService

        materia_id = await crear_materia(db_session, tenant_id)
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)

        service = FechaAcademicaService(db_session, tenant_id)
        f1 = await service.create_fecha(materia_id=materia_id, cohorte_id=cohorte_id, tipo=TipoFechaAcademica.PARCIAL, numero=1, periodo="2026-1C", fecha=date(2026, 5, 15), titulo="Parcial")
        f2 = await service.create_fecha(materia_id=materia_id, cohorte_id=cohorte_id, tipo=TipoFechaAcademica.TP, numero=1, periodo="2026-1C", fecha=date(2026, 6, 1), titulo="TP")

        assert f1.id != f2.id

    async def test_list_fechas(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.programas import TipoFechaAcademica
        from app.services.fecha_academica_service import FechaAcademicaService

        materia_id = await crear_materia(db_session, tenant_id)
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)

        service = FechaAcademicaService(db_session, tenant_id)
        await service.create_fecha(materia_id=materia_id, cohorte_id=cohorte_id, tipo=TipoFechaAcademica.PARCIAL, numero=1, periodo="2026-1C", fecha=date(2026, 5, 15), titulo="Parcial")
        await service.create_fecha(materia_id=materia_id, cohorte_id=cohorte_id, tipo=TipoFechaAcademica.TP, numero=1, periodo="2026-1C", fecha=date(2026, 6, 1), titulo="TP")

        fechas = await service.list_fechas()
        assert len(fechas) == 2

        by_materia = await service.list_fechas(materia_id=materia_id)
        assert len(by_materia) == 2

        by_tipo = await service.list_fechas(tipo=TipoFechaAcademica.PARCIAL)
        assert len(by_tipo) == 1

    async def test_list_calendario(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.programas import TipoFechaAcademica
        from app.services.fecha_academica_service import FechaAcademicaService

        materia_id = await crear_materia(db_session, tenant_id)
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)

        service = FechaAcademicaService(db_session, tenant_id)
        f2 = await service.create_fecha(materia_id=materia_id, cohorte_id=cohorte_id, tipo=TipoFechaAcademica.TP, numero=1, periodo="2026-1C", fecha=date(2026, 7, 1), titulo="Julio")
        f1 = await service.create_fecha(materia_id=materia_id, cohorte_id=cohorte_id, tipo=TipoFechaAcademica.PARCIAL, numero=1, periodo="2026-1C", fecha=date(2026, 5, 15), titulo="Mayo")

        calendario = await service.list_calendario(desde=date(2026, 1, 1), hasta=date(2026, 12, 31))
        assert [f.id for f in calendario] == [f1.id, f2.id]

    async def test_update_fecha(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.programas import TipoFechaAcademica
        from app.services.fecha_academica_service import FechaAcademicaService

        materia_id = await crear_materia(db_session, tenant_id)
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)

        service = FechaAcademicaService(db_session, tenant_id)
        created = await service.create_fecha(materia_id=materia_id, cohorte_id=cohorte_id, tipo=TipoFechaAcademica.PARCIAL, numero=1, periodo="2026-1C", fecha=date(2026, 5, 15), titulo="Original")

        updated = await service.update_fecha(created.id, titulo="Updated", fecha=date(2026, 5, 20))
        assert updated.titulo == "Updated"
        assert updated.fecha == date(2026, 5, 20)

    async def test_delete_fecha_soft_delete(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.programas import TipoFechaAcademica
        from app.services.fecha_academica_service import FechaAcademicaService, FechaNotFoundError

        materia_id = await crear_materia(db_session, tenant_id)
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)

        service = FechaAcademicaService(db_session, tenant_id)
        created = await service.create_fecha(materia_id=materia_id, cohorte_id=cohorte_id, tipo=TipoFechaAcademica.PARCIAL, numero=1, periodo="2026-1C", fecha=date(2026, 5, 15), titulo="To Delete")

        assert await service.get_fecha(created.id) is not None
        await service.delete_fecha(created.id)
        with pytest.raises(FechaNotFoundError):
            await service.get_fecha(created.id)

    async def test_generate_lms_fragment_con_fechas(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.programas import TipoFechaAcademica
        from app.services.fecha_academica_service import FechaAcademicaService

        materia_id = await crear_materia(db_session, tenant_id)
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)

        service = FechaAcademicaService(db_session, tenant_id)
        await service.create_fecha(materia_id=materia_id, cohorte_id=cohorte_id, tipo=TipoFechaAcademica.PARCIAL, numero=1, periodo="2026-1C", fecha=date(2026, 5, 15), titulo="Primer Parcial")

        fragment = await service.generate_lms_fragment(materia_id=materia_id, cohorte_id=cohorte_id)
        assert "<table>" in fragment
        assert "Primer Parcial" in fragment
        assert "2026-05-15" in fragment

    async def test_generate_lms_fragment_sin_fechas(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID
    ) -> None:
        from app.services.fecha_academica_service import FechaAcademicaService

        materia_id = await crear_materia(db_session, tenant_id)
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)

        service = FechaAcademicaService(db_session, tenant_id)
        fragment = await service.generate_lms_fragment(materia_id=materia_id, cohorte_id=cohorte_id)
        assert "No hay fechas académicas programadas." in fragment

    async def test_generate_lms_fragment_orden_cronologico(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.programas import TipoFechaAcademica
        from app.services.fecha_academica_service import FechaAcademicaService

        materia_id = await crear_materia(db_session, tenant_id)
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)

        service = FechaAcademicaService(db_session, tenant_id)
        await service.create_fecha(materia_id=materia_id, cohorte_id=cohorte_id, tipo=TipoFechaAcademica.TP, numero=1, periodo="2026-1C", fecha=date(2026, 7, 1), titulo="TP Julio")
        await service.create_fecha(materia_id=materia_id, cohorte_id=cohorte_id, tipo=TipoFechaAcademica.PARCIAL, numero=1, periodo="2026-1C", fecha=date(2026, 5, 15), titulo="Parcial Mayo")
        await service.create_fecha(materia_id=materia_id, cohorte_id=cohorte_id, tipo=TipoFechaAcademica.COLOQUIO, numero=1, periodo="2026-1C", fecha=date(2026, 3, 1), titulo="Coloquio Marzo")

        fragment = await service.generate_lms_fragment(materia_id=materia_id, cohorte_id=cohorte_id)
        mayo_pos = fragment.index("Mayo")
        julio_pos = fragment.index("Julio")
        marzo_pos = fragment.index("Marzo")
        assert marzo_pos < mayo_pos < julio_pos
