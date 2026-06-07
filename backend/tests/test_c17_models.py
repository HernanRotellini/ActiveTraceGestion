"""Tests para C-17 Programas y Fechas Académicas: ProgramaMateria, FechaAcademica.

Strict TDD: RED -> GREEN -> TRIANGULATE -> REFACTOR.
"""

from datetime import date
from uuid import UUID, uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base


@pytest.fixture
async def c17_schema(db_engine: None):
    """Creates a fresh schema for C-17 tests."""
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

    tenant = Tenant(id=uuid4(), name="Tenant C17", code=f"c17-{uuid4().hex[:8]}")
    db_session.add(tenant)
    await db_session.flush()
    return tenant.id


@pytest.fixture
async def otro_tenant_id(db_session: AsyncSession, c17_schema: None) -> UUID:
    from app.models.tenant import Tenant

    tenant = Tenant(id=uuid4(), name="Otro Tenant C17", code=f"c17-other-{uuid4().hex[:8]}")
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


class TestProgramaMateriaModel:
    async def test_crear_programa_con_contexto_valido(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.programas import ProgramaMateria

        materia_id = await crear_materia(db_session, tenant_id, codigo="MAT-PROG")
        carrera_id = await crear_carrera(db_session, tenant_id, codigo="CAR-PROG")
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id, nombre="Coh-2026")

        programa = ProgramaMateria(
            tenant_id=tenant_id,
            materia_id=materia_id,
            carrera_id=carrera_id,
            cohorte_id=cohorte_id,
            titulo="Programa Analítico 2026",
            referencia_archivo="/files/programa_2026.pdf",
        )
        db_session.add(programa)
        await db_session.flush()

        assert programa.tenant_id == tenant_id
        assert programa.materia_id == materia_id
        assert programa.carrera_id == carrera_id
        assert programa.cohorte_id == cohorte_id
        assert programa.titulo == "Programa Analítico 2026"
        assert programa.referencia_archivo == "/files/programa_2026.pdf"
        assert programa.deleted_at is None
        assert programa.created_at is not None
        assert programa.updated_at is not None

    async def test_programa_requiere_campos_obligatorios(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.programas import ProgramaMateria

        materia_id = await crear_materia(db_session, tenant_id)
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)

        programa = ProgramaMateria(
            tenant_id=tenant_id,
            materia_id=materia_id,
            carrera_id=carrera_id,
            cohorte_id=cohorte_id,
        )
        db_session.add(programa)
        with pytest.raises(IntegrityError):
            await db_session.flush()
        await db_session.rollback()

    async def test_programa_soft_delete_excluye(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.programas import ProgramaMateria
        from app.repositories.base import TenantScopedRepository

        materia_id = await crear_materia(db_session, tenant_id)
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)

        p1 = ProgramaMateria(
            tenant_id=tenant_id, materia_id=materia_id, carrera_id=carrera_id,
            cohorte_id=cohorte_id, titulo="Programa Activo",
            referencia_archivo="/files/activo.pdf",
        )
        p2 = ProgramaMateria(
            tenant_id=tenant_id, materia_id=materia_id, carrera_id=carrera_id,
            cohorte_id=cohorte_id, titulo="Programa a Borrar",
            referencia_archivo="/files/borrar.pdf",
        )
        db_session.add_all([p1, p2])
        await db_session.flush()

        repo = TenantScopedRepository(db_session, ProgramaMateria, tenant_id)
        await repo.soft_delete(p2.id)
        await db_session.flush()

        active = await repo.list()
        assert [p.id for p in active] == [p1.id]

    async def test_programa_duplicado_titulo_rechazado(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.programas import ProgramaMateria

        materia_id = await crear_materia(db_session, tenant_id)
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)

        p1 = ProgramaMateria(
            tenant_id=tenant_id, materia_id=materia_id, carrera_id=carrera_id,
            cohorte_id=cohorte_id, titulo="Programa Unico",
            referencia_archivo="/files/p1.pdf",
        )
        db_session.add(p1)
        await db_session.flush()

        p2 = ProgramaMateria(
            tenant_id=tenant_id, materia_id=materia_id, carrera_id=carrera_id,
            cohorte_id=cohorte_id, titulo="Programa Unico",
            referencia_archivo="/files/p2.pdf",
        )
        db_session.add(p2)
        with pytest.raises(IntegrityError):
            await db_session.flush()
        await db_session.rollback()

    async def test_programa_mismo_titulo_diferente_materia_ok(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.programas import ProgramaMateria

        m1 = await crear_materia(db_session, tenant_id, codigo="MAT-UNO")
        m2 = await crear_materia(db_session, tenant_id, codigo="MAT-DOS")
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)

        p1 = ProgramaMateria(
            tenant_id=tenant_id, materia_id=m1, carrera_id=carrera_id,
            cohorte_id=cohorte_id, titulo="Mismo Titulo",
            referencia_archivo="/files/p1.pdf",
        )
        p2 = ProgramaMateria(
            tenant_id=tenant_id, materia_id=m2, carrera_id=carrera_id,
            cohorte_id=cohorte_id, titulo="Mismo Titulo",
            referencia_archivo="/files/p2.pdf",
        )
        db_session.add_all([p1, p2])
        await db_session.flush()
        assert p1.id != p2.id

    async def test_programa_cross_tenant_aislamiento(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID, otro_tenant_id: UUID
    ) -> None:
        from app.models.programas import ProgramaMateria
        from app.repositories.base import TenantScopedRepository

        m1 = await crear_materia(db_session, tenant_id)
        c1 = await crear_carrera(db_session, tenant_id)
        co1 = await crear_cohorte(db_session, tenant_id, c1)

        m2 = await crear_materia(db_session, otro_tenant_id, codigo="MAT-OTHER")
        c2 = await crear_carrera(db_session, otro_tenant_id, codigo="CAR-OTHER")
        co2 = await crear_cohorte(db_session, otro_tenant_id, c2, nombre="Other-Coh")

        p1 = ProgramaMateria(
            tenant_id=tenant_id, materia_id=m1, carrera_id=c1,
            cohorte_id=co1, titulo="T1", referencia_archivo="/files/t1.pdf",
        )
        p2 = ProgramaMateria(
            tenant_id=otro_tenant_id, materia_id=m2, carrera_id=c2,
            cohorte_id=co2, titulo="T2", referencia_archivo="/files/t2.pdf",
        )
        db_session.add_all([p1, p2])
        await db_session.flush()

        repo = TenantScopedRepository(db_session, ProgramaMateria, tenant_id)
        active = await repo.list()
        assert len(active) == 1
        assert active[0].titulo == "T1"


class TestFechaAcademicaModel:
    async def test_crear_fecha_con_contexto_y_tipo(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.programas import FechaAcademica, TipoFechaAcademica

        materia_id = await crear_materia(db_session, tenant_id)
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)

        fecha = FechaAcademica(
            tenant_id=tenant_id,
            materia_id=materia_id,
            cohorte_id=cohorte_id,
            tipo=TipoFechaAcademica.PARCIAL,
            numero=1,
            periodo="2026-1C",
            fecha=date(2026, 5, 15),
            titulo="Primer Parcial",
        )
        db_session.add(fecha)
        await db_session.flush()

        assert fecha.tenant_id == tenant_id
        assert fecha.materia_id == materia_id
        assert fecha.cohorte_id == cohorte_id
        assert fecha.tipo == TipoFechaAcademica.PARCIAL
        assert fecha.numero == 1
        assert fecha.periodo == "2026-1C"
        assert fecha.fecha == date(2026, 5, 15)
        assert fecha.titulo == "Primer Parcial"
        assert fecha.deleted_at is None

    async def test_fecha_duplicado_rechazado(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.programas import FechaAcademica, TipoFechaAcademica

        materia_id = await crear_materia(db_session, tenant_id)
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)

        f1 = FechaAcademica(
            tenant_id=tenant_id, materia_id=materia_id, cohorte_id=cohorte_id,
            tipo=TipoFechaAcademica.PARCIAL, numero=1, periodo="2026-1C",
            fecha=date(2026, 5, 15), titulo="Primer Parcial",
        )
        db_session.add(f1)
        await db_session.flush()

        f2 = FechaAcademica(
            tenant_id=tenant_id, materia_id=materia_id, cohorte_id=cohorte_id,
            tipo=TipoFechaAcademica.PARCIAL, numero=1, periodo="2026-1C",
            fecha=date(2026, 5, 15), titulo="Primer Parcial Duplicado",
        )
        db_session.add(f2)
        with pytest.raises(IntegrityError):
            await db_session.flush()
        await db_session.rollback()

    async def test_fecha_duplicado_mismo_contexto_rechazado(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.programas import FechaAcademica, TipoFechaAcademica

        materia_id = await crear_materia(db_session, tenant_id)
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)

        f1 = FechaAcademica(
            tenant_id=tenant_id, materia_id=materia_id, cohorte_id=cohorte_id,
            tipo=TipoFechaAcademica.PARCIAL, numero=1, periodo="2026-1C",
            fecha=date(2026, 5, 15), titulo="Original",
        )
        db_session.add(f1)
        await db_session.flush()

        f2 = FechaAcademica(
            tenant_id=tenant_id, materia_id=materia_id, cohorte_id=cohorte_id,
            tipo=TipoFechaAcademica.PARCIAL, numero=1, periodo="2026-1C",
            fecha=date(2026, 6, 1), titulo="Duplicado Contexto",
        )
        db_session.add(f2)
        with pytest.raises(IntegrityError):
            await db_session.flush()
        await db_session.rollback()

    async def test_fecha_misma_materia_diferente_tipo_ok(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.programas import FechaAcademica, TipoFechaAcademica

        materia_id = await crear_materia(db_session, tenant_id)
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)

        f1 = FechaAcademica(
            tenant_id=tenant_id, materia_id=materia_id, cohorte_id=cohorte_id,
            tipo=TipoFechaAcademica.PARCIAL, numero=1, periodo="2026-1C",
            fecha=date(2026, 5, 15), titulo="Parcial",
        )
        f2 = FechaAcademica(
            tenant_id=tenant_id, materia_id=materia_id, cohorte_id=cohorte_id,
            tipo=TipoFechaAcademica.TP, numero=1, periodo="2026-1C",
            fecha=date(2026, 6, 1), titulo="TP",
        )
        db_session.add_all([f1, f2])
        await db_session.flush()
        assert f1.id != f2.id

    async def test_fecha_soft_delete_excluye(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.programas import FechaAcademica, TipoFechaAcademica
        from app.repositories.base import TenantScopedRepository

        materia_id = await crear_materia(db_session, tenant_id)
        carrera_id = await crear_carrera(db_session, tenant_id)
        cohorte_id = await crear_cohorte(db_session, tenant_id, carrera_id)

        f1 = FechaAcademica(
            tenant_id=tenant_id, materia_id=materia_id, cohorte_id=cohorte_id,
            tipo=TipoFechaAcademica.PARCIAL, numero=1, periodo="2026-1C",
            fecha=date(2026, 5, 15), titulo="Visible",
        )
        f2 = FechaAcademica(
            tenant_id=tenant_id, materia_id=materia_id, cohorte_id=cohorte_id,
            tipo=TipoFechaAcademica.TP, numero=1, periodo="2026-1C",
            fecha=date(2026, 6, 1), titulo="Oculto",
        )
        db_session.add_all([f1, f2])
        await db_session.flush()

        repo = TenantScopedRepository(db_session, FechaAcademica, tenant_id)
        await repo.soft_delete(f2.id)
        await db_session.flush()

        active = await repo.list()
        assert [f.id for f in active] == [f1.id]

    async def test_fecha_cross_tenant_aislamiento(
        self, db_session: AsyncSession, c17_schema: None, tenant_id: UUID, otro_tenant_id: UUID
    ) -> None:
        from app.models.programas import FechaAcademica, TipoFechaAcademica
        from app.repositories.base import TenantScopedRepository

        m1 = await crear_materia(db_session, tenant_id)
        c1 = await crear_carrera(db_session, tenant_id)
        co1 = await crear_cohorte(db_session, tenant_id, c1)
        m2 = await crear_materia(db_session, otro_tenant_id, codigo="MAT-FECH")
        c2 = await crear_carrera(db_session, otro_tenant_id, codigo="CAR-FECH")
        co2 = await crear_cohorte(db_session, otro_tenant_id, c2, nombre="FECH-Coh")

        f1 = FechaAcademica(
            tenant_id=tenant_id, materia_id=m1, cohorte_id=co1,
            tipo=TipoFechaAcademica.PARCIAL, numero=1, periodo="2026-1C",
            fecha=date(2026, 5, 15), titulo="T1",
        )
        f2 = FechaAcademica(
            tenant_id=otro_tenant_id, materia_id=m2, cohorte_id=co2,
            tipo=TipoFechaAcademica.PARCIAL, numero=1, periodo="2026-1C",
            fecha=date(2026, 5, 15), titulo="T2",
        )
        db_session.add_all([f1, f2])
        await db_session.flush()

        repo = TenantScopedRepository(db_session, FechaAcademica, tenant_id)
        active = await repo.list()
        assert len(active) == 1
        assert active[0].titulo == "T1"

    async def test_tipo_fecha_academica_enum_values(self) -> None:
        from app.models.programas import TipoFechaAcademica

        values = [item.value for item in TipoFechaAcademica]
        assert "Parcial" in values
        assert "TP" in values
        assert "Coloquio" in values
        assert "Recuperatorio" in values
