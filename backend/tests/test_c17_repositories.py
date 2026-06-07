"""Tests para C-17 repositories: ProgramaMateriaRepository, FechaAcademicaRepository.

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
    """Creates a fresh schema for C-17 repository tests."""
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

    tenant = Tenant(id=uuid4(), name="Tenant C17 Repo", code=f"c17r-{uuid4().hex[:8]}")
    db_session.add(tenant)
    await db_session.flush()
    return tenant.id


@pytest.fixture
async def otro_tenant_id(db_session: AsyncSession, c17_schema: None) -> UUID:
    from app.models.tenant import Tenant

    tenant = Tenant(id=uuid4(), name="Otro Tenant C17 Repo", code=f"c17r-other-{uuid4().hex[:8]}")
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


class TestProgramaMateriaRepository:
    async def test_create_get_programa(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID
    ) -> None:
        from app.repositories.programa_repository import ProgramaMateriaRepository

        materia_id = await crear_materia(db_session, tenant_id)
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)

        repo = ProgramaMateriaRepository(db_session, tenant_id)
        programa = await repo.create(
            materia_id=materia_id,
            carrera_id=carrera_id,
            cohorte_id=cohorte_id,
            titulo="Programa Analítico",
            referencia_archivo="/files/programa.pdf",
        )

        assert programa.titulo == "Programa Analítico"
        assert programa.tenant_id == tenant_id

        fetched = await repo.get(programa.id)
        assert fetched is not None
        assert fetched.id == programa.id

    async def test_list_programas_active(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID
    ) -> None:
        from app.repositories.programa_repository import ProgramaMateriaRepository

        materia_id = await crear_materia(db_session, tenant_id)
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)

        repo = ProgramaMateriaRepository(db_session, tenant_id)
        p1 = await repo.create(materia_id=materia_id, carrera_id=carrera_id, cohorte_id=cohorte_id, titulo="P1", referencia_archivo="/f1.pdf")
        p2 = await repo.create(materia_id=materia_id, carrera_id=carrera_id, cohorte_id=cohorte_id, titulo="P2", referencia_archivo="/f2.pdf")
        p3 = await repo.create(materia_id=materia_id, carrera_id=carrera_id, cohorte_id=cohorte_id, titulo="P3", referencia_archivo="/f3.pdf")

        await repo.soft_delete(p2.id)
        await db_session.flush()

        active = await repo.list()
        assert len(active) == 2
        active_ids = {a.id for a in active}
        assert p1.id in active_ids
        assert p3.id in active_ids
        assert p2.id not in active_ids

    async def test_list_programas_filtros(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID
    ) -> None:
        from app.repositories.programa_repository import ProgramaMateriaRepository

        m1 = await crear_materia(db_session, tenant_id, codigo="MAT-F1")
        m2 = await crear_materia(db_session, tenant_id, codigo="MAT-F2")
        c1 = await crear_carrera(db_session, tenant_id, codigo="CAR-F1")
        c2 = await crear_carrera(db_session, tenant_id, codigo="CAR-F2")
        co1 = await crear_cohorte(db_session, tenant_id, c1, nombre="Coh-F1")
        co2 = await crear_cohorte(db_session, tenant_id, c2, nombre="Coh-F2")

        repo = ProgramaMateriaRepository(db_session, tenant_id)
        await repo.create(materia_id=m1, carrera_id=c1, cohorte_id=co1, titulo="P1", referencia_archivo="/f1.pdf")
        await repo.create(materia_id=m2, carrera_id=c2, cohorte_id=co2, titulo="P2", referencia_archivo="/f2.pdf")

        by_materia = await repo.list_filtered(materia_id=m1)
        assert len(by_materia) == 1
        assert by_materia[0].titulo == "P1"

        by_carrera = await repo.list_filtered(carrera_id=c1)
        assert len(by_carrera) == 1

        by_cohorte = await repo.list_filtered(cohorte_id=co1)
        assert len(by_cohorte) == 1

        all_items = await repo.list_filtered()
        assert len(all_items) == 2

    async def test_update_programa(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID
    ) -> None:
        from app.repositories.programa_repository import ProgramaMateriaRepository

        materia_id = await crear_materia(db_session, tenant_id)
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)

        repo = ProgramaMateriaRepository(db_session, tenant_id)
        programa = await repo.create(materia_id=materia_id, carrera_id=carrera_id, cohorte_id=cohorte_id, titulo="Original", referencia_archivo="/orig.pdf")

        updated = await repo.update(programa.id, titulo="Updated", referencia_archivo="/new.pdf")
        assert updated is not None
        assert updated.titulo == "Updated"
        assert updated.referencia_archivo == "/new.pdf"

    async def test_soft_delete_programa(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID
    ) -> None:
        from app.repositories.programa_repository import ProgramaMateriaRepository

        materia_id = await crear_materia(db_session, tenant_id)
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)

        repo = ProgramaMateriaRepository(db_session, tenant_id)
        programa = await repo.create(materia_id=materia_id, carrera_id=carrera_id, cohorte_id=cohorte_id, titulo="To Delete", referencia_archivo="/del.pdf")

        assert await repo.get(programa.id) is not None
        assert await repo.soft_delete(programa.id) is True
        await db_session.flush()
        assert await repo.get(programa.id) is None

    async def test_cross_tenant_no_see(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID, otro_tenant_id: UUID
    ) -> None:
        from app.repositories.programa_repository import ProgramaMateriaRepository

        m1 = await crear_materia(db_session, tenant_id)
        c1 = await crear_carrera(db_session, tenant_id)
        co1 = await crear_cohorte(db_session, tenant_id, c1)
        m2 = await crear_materia(db_session, otro_tenant_id, codigo="MAT-X")
        c2 = await crear_carrera(db_session, otro_tenant_id, codigo="CAR-X")
        co2 = await crear_cohorte(db_session, otro_tenant_id, c2, nombre="Coh-X")

        repo_a = ProgramaMateriaRepository(db_session, tenant_id)
        repo_b = ProgramaMateriaRepository(db_session, otro_tenant_id)

        p1 = await repo_a.create(materia_id=m1, carrera_id=c1, cohorte_id=co1, titulo="T1", referencia_archivo="/t1.pdf")
        p2 = await repo_b.create(materia_id=m2, carrera_id=c2, cohorte_id=co2, titulo="T2", referencia_archivo="/t2.pdf")

        assert await repo_a.get(p2.id) is None
        assert await repo_b.get(p1.id) is None

        a_list = await repo_a.list()
        assert [p.id for p in a_list] == [p1.id]


class TestFechaAcademicaRepository:
    async def test_create_get_fecha(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.programas import TipoFechaAcademica
        from app.repositories.fecha_academica_repository import FechaAcademicaRepository

        materia_id = await crear_materia(db_session, tenant_id)
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)

        repo = FechaAcademicaRepository(db_session, tenant_id)
        fecha = await repo.create(
            materia_id=materia_id,
            cohorte_id=cohorte_id,
            tipo=TipoFechaAcademica.PARCIAL,
            numero=1,
            periodo="2026-1C",
            fecha=date(2026, 5, 15),
            titulo="Primer Parcial",
        )

        assert fecha.titulo == "Primer Parcial"
        assert fecha.tenant_id == tenant_id
        assert fecha.tipo == TipoFechaAcademica.PARCIAL

        fetched = await repo.get(fecha.id)
        assert fetched is not None
        assert fetched.id == fecha.id

    async def test_list_fechas_active(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.programas import TipoFechaAcademica
        from app.repositories.fecha_academica_repository import FechaAcademicaRepository

        materia_id = await crear_materia(db_session, tenant_id)
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)

        repo = FechaAcademicaRepository(db_session, tenant_id)
        f1 = await repo.create(materia_id=materia_id, cohorte_id=cohorte_id, tipo=TipoFechaAcademica.PARCIAL, numero=1, periodo="2026-1C", fecha=date(2026, 5, 15), titulo="Visible")
        f2 = await repo.create(materia_id=materia_id, cohorte_id=cohorte_id, tipo=TipoFechaAcademica.TP, numero=1, periodo="2026-1C", fecha=date(2026, 6, 1), titulo="Oculto")

        await repo.soft_delete(f2.id)
        await db_session.flush()

        active = await repo.list()
        assert [f.id for f in active] == [f1.id]

    async def test_list_fechas_filtros(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.programas import TipoFechaAcademica
        from app.repositories.fecha_academica_repository import FechaAcademicaRepository

        m1 = await crear_materia(db_session, tenant_id, codigo="MAT-FILTRO-F1")
        m2 = await crear_materia(db_session, tenant_id, codigo="MAT-FILTRO-F2")
        carrera_id = await crear_carrera(db_session, tenant_id)
        co1 = await crear_cohorte(db_session, tenant_id, carrera_id, nombre="Coh-Filtro-1")
        co2 = await crear_cohorte(db_session, tenant_id, carrera_id, nombre="Coh-Filtro-2")

        repo = FechaAcademicaRepository(db_session, tenant_id)
        await repo.create(materia_id=m1, cohorte_id=co1, tipo=TipoFechaAcademica.PARCIAL, numero=1, periodo="2026-1C", fecha=date(2026, 5, 15), titulo="F1")
        await repo.create(materia_id=m2, cohorte_id=co2, tipo=TipoFechaAcademica.TP, numero=1, periodo="2026-1C", fecha=date(2026, 6, 1), titulo="F2")

        by_materia = await repo.list_filtered(materia_id=m1)
        assert len(by_materia) == 1
        assert by_materia[0].titulo == "F1"

        by_cohorte = await repo.list_filtered(cohorte_id=co1)
        assert len(by_cohorte) == 1

        by_tipo = await repo.list_filtered(tipo=TipoFechaAcademica.PARCIAL)
        assert len(by_tipo) == 1

        by_periodo = await repo.list_filtered(periodo="2026-1C")
        assert len(by_periodo) == 2

    async def test_list_fechas_date_range(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.programas import TipoFechaAcademica
        from app.repositories.fecha_academica_repository import FechaAcademicaRepository

        materia_id = await crear_materia(db_session, tenant_id)
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)

        repo = FechaAcademicaRepository(db_session, tenant_id)
        f1 = await repo.create(materia_id=materia_id, cohorte_id=cohorte_id, tipo=TipoFechaAcademica.PARCIAL, numero=1, periodo="2026-1C", fecha=date(2026, 5, 15), titulo="Mayo")
        await repo.create(materia_id=materia_id, cohorte_id=cohorte_id, tipo=TipoFechaAcademica.TP, numero=1, periodo="2026-1C", fecha=date(2026, 7, 1), titulo="Julio")

        in_range = await repo.list_by_date_range(desde=date(2026, 5, 1), hasta=date(2026, 6, 30))
        assert [f.id for f in in_range] == [f1.id]

    async def test_list_calendario(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.programas import TipoFechaAcademica
        from app.repositories.fecha_academica_repository import FechaAcademicaRepository

        materia_id = await crear_materia(db_session, tenant_id)
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)

        repo = FechaAcademicaRepository(db_session, tenant_id)
        f2 = await repo.create(materia_id=materia_id, cohorte_id=cohorte_id, tipo=TipoFechaAcademica.TP, numero=1, periodo="2026-1C", fecha=date(2026, 7, 1), titulo="Julio")
        f1 = await repo.create(materia_id=materia_id, cohorte_id=cohorte_id, tipo=TipoFechaAcademica.PARCIAL, numero=1, periodo="2026-1C", fecha=date(2026, 5, 15), titulo="Mayo")

        calendario = await repo.list_for_calendar(desde=date(2026, 1, 1), hasta=date(2026, 12, 31))
        assert [f.id for f in calendario] == [f1.id, f2.id]

    async def test_update_fecha(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.programas import TipoFechaAcademica
        from app.repositories.fecha_academica_repository import FechaAcademicaRepository

        materia_id = await crear_materia(db_session, tenant_id)
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)

        repo = FechaAcademicaRepository(db_session, tenant_id)
        fecha = await repo.create(materia_id=materia_id, cohorte_id=cohorte_id, tipo=TipoFechaAcademica.PARCIAL, numero=1, periodo="2026-1C", fecha=date(2026, 5, 15), titulo="Original")

        updated = await repo.update(fecha.id, titulo="Updated", fecha=date(2026, 5, 20))
        assert updated is not None
        assert updated.titulo == "Updated"
        assert updated.fecha == date(2026, 5, 20)

    async def test_soft_delete_fecha(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.programas import TipoFechaAcademica
        from app.repositories.fecha_academica_repository import FechaAcademicaRepository

        materia_id = await crear_materia(db_session, tenant_id)
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)

        repo = FechaAcademicaRepository(db_session, tenant_id)
        fecha = await repo.create(materia_id=materia_id, cohorte_id=cohorte_id, tipo=TipoFechaAcademica.PARCIAL, numero=1, periodo="2026-1C", fecha=date(2026, 5, 15), titulo="To Delete")

        assert await repo.get(fecha.id) is not None
        assert await repo.soft_delete(fecha.id) is True
        await db_session.flush()
        assert await repo.get(fecha.id) is None

    async def test_cross_tenant_aislamiento(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID, otro_tenant_id: UUID
    ) -> None:
        from app.models.programas import TipoFechaAcademica
        from app.repositories.fecha_academica_repository import FechaAcademicaRepository

        m1 = await crear_materia(db_session, tenant_id)
        c1 = await crear_carrera(db_session, tenant_id)
        co1 = await crear_cohorte(db_session, tenant_id, c1)
        m2 = await crear_materia(db_session, otro_tenant_id, codigo="MAT-FX")
        c2 = await crear_carrera(db_session, otro_tenant_id, codigo="CAR-FX")
        co2 = await crear_cohorte(db_session, otro_tenant_id, c2, nombre="Coh-FX")

        repo_a = FechaAcademicaRepository(db_session, tenant_id)
        repo_b = FechaAcademicaRepository(db_session, otro_tenant_id)

        f1 = await repo_a.create(materia_id=m1, cohorte_id=co1, tipo=TipoFechaAcademica.PARCIAL, numero=1, periodo="2026-1C", fecha=date(2026, 5, 15), titulo="T1")
        f2 = await repo_b.create(materia_id=m2, cohorte_id=co2, tipo=TipoFechaAcademica.PARCIAL, numero=1, periodo="2026-1C", fecha=date(2026, 5, 15), titulo="T2")

        assert await repo_a.get(f2.id) is None
        assert await repo_b.get(f1.id) is None
