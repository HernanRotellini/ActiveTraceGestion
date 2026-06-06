"""Tests para C-15 Avisos y Acknowledgment.

Strict TDD: RED → GREEN → TRIANGULATE → REFACTOR.
Cobertura mínima: ≥80% líneas, ≥90% reglas de negocio (RN-18/19/20).
"""

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

# ═══════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════


@pytest.fixture
async def aviso_schema(db_engine: None):
    """Creates full schema for avisos tests."""
    from app.models.aviso import AcknowledgmentAviso, Aviso  # noqa: F401
    from app.models.estructura_academica import Carrera, Cohorte, Materia  # noqa: F401
    from app.models.tenant import Tenant  # noqa: F401
    from app.models.usuarios_asignaciones import Asignacion, Usuario  # noqa: F401

    from app.core.database import get_sessionmaker as _gsm
    sessionmaker = _gsm()
    async with sessionmaker() as session:
        connection = await session.connection()
        await connection.execute(
            text(
                "DROP TABLE IF EXISTS acknowledgments_aviso, avisos, "
                "asignaciones, usuarios, cohortes, carreras, materias, "
                "tenants CASCADE"
            )
        )
        await connection.execute(text("DROP TYPE IF EXISTS alcance_aviso CASCADE"))
        await connection.execute(text("DROP TYPE IF EXISTS severidad_aviso CASCADE"))
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
        await session.commit()


@pytest.fixture
async def tenant_id(db_session: AsyncSession, aviso_schema: None) -> UUID:
    """Crea un tenant de prueba y retorna su id."""
    from app.models.tenant import Tenant

    tenant = Tenant(id=uuid4(), name="Test Tenant")
    db_session.add(tenant)
    await db_session.flush()
    return tenant.id


@pytest.fixture
async def otro_tenant_id(db_session: AsyncSession, aviso_schema: None) -> UUID:
    """Crea otro tenant para tests de aislamiento."""
    from app.models.tenant import Tenant

    tenant = Tenant(id=uuid4(), name="Other Tenant")
    db_session.add(tenant)
    await db_session.flush()
    return tenant.id


@pytest.fixture
async def materia_id(db_session: AsyncSession, tenant_id: UUID) -> UUID:
    """Crea una materia de prueba."""
    from app.models.estructura_academica import Materia

    materia = Materia(tenant_id=tenant_id, codigo="TEST_01", nombre="Materia Test")
    db_session.add(materia)
    await db_session.flush()
    return materia.id


@pytest.fixture
async def cohorte_id(db_session: AsyncSession, tenant_id: UUID) -> UUID:
    """Crea una cohorte de prueba."""
    from app.models.estructura_academica import Carrera, Cohorte

    carrera = Carrera(tenant_id=tenant_id, codigo="CARR_01", nombre="Carrera Test")
    db_session.add(carrera)
    await db_session.flush()

    cohorte = Cohorte(
        tenant_id=tenant_id, carrera_id=carrera.id, nombre="2026-1", anio=2026,
    )
    db_session.add(cohorte)
    await db_session.flush()
    return cohorte.id


@pytest.fixture
async def usuario_id(db_session: AsyncSession, tenant_id: UUID) -> UUID:
    """Crea un usuario de prueba."""
    from app.models.usuarios_asignaciones import Usuario

    usuario = Usuario(
        tenant_id=tenant_id,
        nombre="Test",
        apellidos="User",
        email="test@test.com",
    )
    db_session.add(usuario)
    await db_session.flush()
    return usuario.id


@pytest.fixture
async def otro_usuario_id(db_session: AsyncSession, tenant_id: UUID) -> UUID:
    """Crea otro usuario de prueba."""
    from app.models.usuarios_asignaciones import Usuario

    usuario = Usuario(
        tenant_id=tenant_id,
        nombre="Other",
        apellidos="User",
        email="other@test.com",
    )
    db_session.add(usuario)
    await db_session.flush()
    return usuario.id


# ═══════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════


async def crear_aviso(
    db_session: AsyncSession,
    tenant_id: UUID,
    **overrides: Any,
) -> UUID:
    """Helper para crear avisos de prueba."""
    from app.models.aviso import Aviso, AlcanceAviso, SeveridadAviso

    defaults: dict[str, Any] = {
        "tenant_id": tenant_id,
        "alcance": AlcanceAviso.GLOBAL,
        "severidad": SeveridadAviso.INFO,
        "titulo": "Aviso de prueba",
        "cuerpo": "Contenido del aviso",
        "inicio_en": datetime.now(UTC) - timedelta(days=1),
        "fin_en": datetime.now(UTC) + timedelta(days=30),
        "orden": 0,
        "activo": True,
        "requiere_ack": False,
    }
    defaults.update(overrides)

    aviso = Aviso(**defaults)
    db_session.add(aviso)
    await db_session.flush()
    return aviso.id


# ═══════════════════════════════════════════════════════════════
# Modelo
# ═══════════════════════════════════════════════════════════════


class TestAvisoModel:
    async def test_crear_aviso_global(
        self, db_session: AsyncSession, aviso_schema: None, tenant_id: UUID,
    ) -> None:
        """Crea un aviso Global exitosamente."""
        aviso_id = await crear_aviso(db_session, tenant_id)
        assert aviso_id is not None

        from app.models.aviso import Aviso
        from sqlalchemy import select

        result = await db_session.execute(
            select(Aviso).where(Aviso.id == aviso_id)
        )
        aviso = result.scalar_one()
        assert aviso.titulo == "Aviso de prueba"
        assert aviso.alcance == "Global"
        assert aviso.activo is True

    async def test_crear_acknowledgment(
        self, db_session: AsyncSession, aviso_schema: None, tenant_id: UUID, usuario_id: UUID,
    ) -> None:
        """Crea un acknowledgment exitosamente."""
        aviso_id = await crear_aviso(db_session, tenant_id, requiere_ack=True)

        from app.models.aviso import AcknowledgmentAviso

        ack = AcknowledgmentAviso(
            tenant_id=tenant_id,
            aviso_id=aviso_id,
            usuario_id=usuario_id,
            confirmado_at=datetime.now(UTC),
        )
        db_session.add(ack)
        await db_session.flush()
        assert ack.id is not None

    async def test_unique_constraint_ack(
        self, db_session: AsyncSession, aviso_schema: None, tenant_id: UUID, usuario_id: UUID,
    ) -> None:
        """Verifica unique constraint (aviso_id, usuario_id)."""
        aviso_id = await crear_aviso(db_session, tenant_id, requiere_ack=True)

        from app.models.aviso import AcknowledgmentAviso

        ack1 = AcknowledgmentAviso(
            tenant_id=tenant_id,
            aviso_id=aviso_id,
            usuario_id=usuario_id,
            confirmado_at=datetime.now(UTC),
        )
        db_session.add(ack1)
        await db_session.flush()

        # Segundo ack mismo par debe fallar
        ack2 = AcknowledgmentAviso(
            tenant_id=tenant_id,
            aviso_id=aviso_id,
            usuario_id=usuario_id,
            confirmado_at=datetime.now(UTC),
        )
        db_session.add(ack2)
        with pytest.raises(Exception):
            await db_session.flush()


# ═══════════════════════════════════════════════════════════════
# Repository: AvisoRepository
# ═══════════════════════════════════════════════════════════════


class TestAvisoRepository:
    async def test_listar_visibles_global(
        self, db_session: AsyncSession, aviso_schema: None, tenant_id: UUID,
    ) -> None:
        """Aviso Global visible para cualquier usuario."""
        await crear_aviso(db_session, tenant_id)

        from app.repositories.aviso_repository import AvisoRepository

        repo = AvisoRepository(db_session, tenant_id)
        avisos = await repo.listar_visibles(roles=["PROFESOR"])
        assert len(avisos) == 1

    async def test_listar_visibles_por_rol(
        self, db_session: AsyncSession, aviso_schema: None, tenant_id: UUID,
    ) -> None:
        """Aviso PorRol visible solo para el rol destino."""
        from app.models.aviso import AlcanceAviso

        await crear_aviso(db_session, tenant_id, alcance=AlcanceAviso.POR_ROL, rol_destino="COORDINADOR")

        from app.repositories.aviso_repository import AvisoRepository

        repo = AvisoRepository(db_session, tenant_id)

        # PROFESOR no lo ve
        avisos_prof = await repo.listar_visibles(roles=["PROFESOR"])
        assert len(avisos_prof) == 0

        # COORDINADOR lo ve
        avisos_coord = await repo.listar_visibles(roles=["COORDINADOR"])
        assert len(avisos_coord) == 1

    async def test_listar_visibles_por_materia(
        self, db_session: AsyncSession, aviso_schema: None, tenant_id: UUID, materia_id: UUID,
    ) -> None:
        """Aviso PorMateria visible solo para usuarios de esa materia."""
        from app.models.aviso import AlcanceAviso

        await crear_aviso(
            db_session, tenant_id,
            alcance=AlcanceAviso.POR_MATERIA, materia_id=materia_id,
        )

        from app.repositories.aviso_repository import AvisoRepository

        repo = AvisoRepository(db_session, tenant_id)

        # Sin materia_ids no lo ve
        avisos_sin = await repo.listar_visibles(roles=["PROFESOR"])
        assert len(avisos_sin) == 0

        # Con materia_id sí lo ve
        avisos_con = await repo.listar_visibles(roles=["PROFESOR"], materia_ids=[materia_id])
        assert len(avisos_con) == 1

    async def test_listar_visibles_por_cohorte(
        self, db_session: AsyncSession, aviso_schema: None, tenant_id: UUID, cohorte_id: UUID,
    ) -> None:
        """Aviso PorCohorte visible solo para usuarios de esa cohorte."""
        from app.models.aviso import AlcanceAviso

        await crear_aviso(
            db_session, tenant_id,
            alcance=AlcanceAviso.POR_COHORTE, cohorte_id=cohorte_id,
        )

        from app.repositories.aviso_repository import AvisoRepository

        repo = AvisoRepository(db_session, tenant_id)

        avisos_sin = await repo.listar_visibles(roles=["PROFESOR"])
        assert len(avisos_sin) == 0

        avisos_con = await repo.listar_visibles(roles=["PROFESOR"], cohorte_ids=[cohorte_id])
        assert len(avisos_con) == 1

    async def test_fuera_de_vigencia_no_visible(
        self, db_session: AsyncSession, aviso_schema: None, tenant_id: UUID,
    ) -> None:
        """Aviso con fin_en pasado no se muestra."""
        await crear_aviso(
            db_session, tenant_id,
            inicio_en=datetime.now(UTC) - timedelta(days=10),
            fin_en=datetime.now(UTC) - timedelta(days=1),
        )

        from app.repositories.aviso_repository import AvisoRepository

        repo = AvisoRepository(db_session, tenant_id)
        avisos = await repo.listar_visibles(roles=["PROFESOR"])
        assert len(avisos) == 0

    async def test_futuro_no_visible(
        self, db_session: AsyncSession, aviso_schema: None, tenant_id: UUID,
    ) -> None:
        """Aviso con inicio_en futuro no se muestra."""
        await crear_aviso(
            db_session, tenant_id,
            inicio_en=datetime.now(UTC) + timedelta(days=10),
        )

        from app.repositories.aviso_repository import AvisoRepository

        repo = AvisoRepository(db_session, tenant_id)
        avisos = await repo.listar_visibles(roles=["PROFESOR"])
        assert len(avisos) == 0

    async def test_inactivo_no_visible(
        self, db_session: AsyncSession, aviso_schema: None, tenant_id: UUID,
    ) -> None:
        """Aviso inactivo (activo=false) no se muestra."""
        await crear_aviso(db_session, tenant_id, activo=False)

        from app.repositories.aviso_repository import AvisoRepository

        repo = AvisoRepository(db_session, tenant_id)
        avisos = await repo.listar_visibles(roles=["PROFESOR"])
        assert len(avisos) == 0

    async def test_orden_prioridad(
        self, db_session: AsyncSession, aviso_schema: None, tenant_id: UUID,
    ) -> None:
        """Avisos ordenados por orden ASC."""
        await crear_aviso(db_session, tenant_id, titulo="Segundo", orden=2)
        await crear_aviso(db_session, tenant_id, titulo="Primero", orden=1)
        await crear_aviso(db_session, tenant_id, titulo="Tercero", orden=3)

        from app.repositories.aviso_repository import AvisoRepository

        repo = AvisoRepository(db_session, tenant_id)
        avisos = await repo.listar_visibles(roles=["PROFESOR"])
        assert len(avisos) == 3
        assert avisos[0].titulo == "Primero"
        assert avisos[1].titulo == "Segundo"
        assert avisos[2].titulo == "Tercero"

    async def test_admin_lista_incluye_inactivos(
        self, db_session: AsyncSession, aviso_schema: None, tenant_id: UUID,
    ) -> None:
        """Listado admin incluye avisos inactivos."""
        await crear_aviso(db_session, tenant_id, titulo="Activo", activo=True)
        await crear_aviso(db_session, tenant_id, titulo="Inactivo", activo=False)

        from app.repositories.aviso_repository import AvisoRepository

        repo = AvisoRepository(db_session, tenant_id)
        avisos = await repo.listar_admin()
        assert len(avisos) == 2

        avisos_activos = await repo.listar_admin(activo=True)
        assert len(avisos_activos) == 1

    async def test_tenant_aislamiento(
        self, db_session: AsyncSession, aviso_schema: None, tenant_id: UUID, otro_tenant_id: UUID,
    ) -> None:
        """Avisos de tenant A no visibles en tenant B."""
        await crear_aviso(db_session, tenant_id, titulo="Aviso A")
        await crear_aviso(db_session, otro_tenant_id, titulo="Aviso B")

        from app.repositories.aviso_repository import AvisoRepository

        repo_a = AvisoRepository(db_session, tenant_id)
        avisos_a = await repo_a.listar_visibles(roles=["PROFESOR"])
        assert len(avisos_a) == 1
        assert avisos_a[0].titulo == "Aviso A"

        repo_b = AvisoRepository(db_session, otro_tenant_id)
        avisos_b = await repo_b.listar_visibles(roles=["PROFESOR"])
        assert len(avisos_b) == 1
        assert avisos_b[0].titulo == "Aviso B"


# ═══════════════════════════════════════════════════════════════
# Repository: AcknowledgmentRepository
# ═══════════════════════════════════════════════════════════════


class TestAcknowledgmentRepository:
    async def test_confirmar_lectura(
        self, db_session: AsyncSession, aviso_schema: None, tenant_id: UUID, usuario_id: UUID,
    ) -> None:
        """Confirmar lectura crea un ack exitosamente."""
        aviso_id = await crear_aviso(db_session, tenant_id, requiere_ack=True)

        from app.repositories.acknowledgment_repository import AcknowledgmentRepository

        repo = AcknowledgmentRepository(db_session, tenant_id)
        ack = await repo.confirmar(aviso_id, usuario_id)
        assert ack is not None
        assert ack.aviso_id == aviso_id

    async def test_confirmar_idempotente(
        self, db_session: AsyncSession, aviso_schema: None, tenant_id: UUID, usuario_id: UUID,
    ) -> None:
        """Segunda confirmación es idempotente (no-op)."""
        aviso_id = await crear_aviso(db_session, tenant_id, requiere_ack=True)

        from app.repositories.acknowledgment_repository import AcknowledgmentRepository

        repo = AcknowledgmentRepository(db_session, tenant_id)
        await repo.confirmar(aviso_id, usuario_id)
        await repo.confirmar(aviso_id, usuario_id)  # No debe fallar

        count = await repo.contar_por_aviso(aviso_id)
        assert count == 1

    async def test_contar_por_aviso(
        self, db_session: AsyncSession, aviso_schema: None, tenant_id: UUID,
        usuario_id: UUID, otro_usuario_id: UUID,
    ) -> None:
        """Contador refleja cantidad de acknowledgments."""
        aviso_id = await crear_aviso(db_session, tenant_id, requiere_ack=True)

        from app.repositories.acknowledgment_repository import AcknowledgmentRepository

        repo = AcknowledgmentRepository(db_session, tenant_id)
        await repo.confirmar(aviso_id, usuario_id)
        await repo.confirmar(aviso_id, otro_usuario_id)

        count = await repo.contar_por_aviso(aviso_id)
        assert count == 2

    async def test_pendientes_ack(
        self, db_session: AsyncSession, aviso_schema: None, tenant_id: UUID,
        usuario_id: UUID, otro_usuario_id: UUID,
    ) -> None:
        """Aviso con requiere_ack aparece en pendientes hasta confirmar."""
        aviso_id = await crear_aviso(db_session, tenant_id, requiere_ack=True, titulo="Requiere Ack")

        from app.repositories.acknowledgment_repository import AcknowledgmentRepository

        repo = AcknowledgmentRepository(db_session, tenant_id)

        # Sin confirmar → aparece en pendientes
        pendientes = await repo.listar_avisos_pendientes_ack(
            usuario_id=usuario_id,
            roles=["PROFESOR"],
        )
        assert len(pendientes) == 1

        # Confirmar
        await repo.confirmar(aviso_id, usuario_id)

        # Ya no aparece en pendientes
        pendientes_after = await repo.listar_avisos_pendientes_ack(
            usuario_id=usuario_id,
            roles=["PROFESOR"],
        )
        assert len(pendientes_after) == 0

        # Otro usuario sigue viéndolo como pendiente
        pendientes_otro = await repo.listar_avisos_pendientes_ack(
            usuario_id=otro_usuario_id,
            roles=["PROFESOR"],
        )
        assert len(pendientes_otro) == 1


# ═══════════════════════════════════════════════════════════════
# Service: AvisoService
# ═══════════════════════════════════════════════════════════════


class TestAvisoService:
    async def test_crear_aviso(
        self, db_session: AsyncSession, aviso_schema: None, tenant_id: UUID, usuario_id: UUID,
    ) -> None:
        """Crear aviso via service."""
        from app.services.aviso_service import AvisoService

        service = AvisoService(db_session, tenant_id)
        now = datetime.now(UTC)

        aviso = await service.crear(
            datos={
                "alcance": "Global",
                "severidad": "Info",
                "titulo": "Aviso service test",
                "cuerpo": "Cuerpo del aviso",
                "inicio_en": now,
                "fin_en": now + timedelta(days=30),
                "orden": 1,
                "activo": True,
                "requiere_ack": False,
            },
            actor_id=usuario_id,
        )
        assert aviso.id is not None
        assert aviso.titulo == "Aviso service test"

    async def test_desactivar_aviso(
        self, db_session: AsyncSession, aviso_schema: None, tenant_id: UUID,
        usuario_id: UUID,
    ) -> None:
        """Desactivar aviso marca activo=false."""
        from app.models.aviso import Aviso
        from sqlalchemy import select

        # Crear aviso directamente
        aviso_id = await crear_aviso(db_session, tenant_id)

        from app.services.aviso_service import AvisoService

        service = AvisoService(db_session, tenant_id)
        await service.desactivar(aviso_id, usuario_id)

        # Verificar que activo=false
        result = await db_session.execute(
            select(Aviso).where(Aviso.id == aviso_id)
        )
        aviso = result.scalar_one()
        assert aviso.activo is False

    async def test_obtener_stats(
        self, db_session: AsyncSession, aviso_schema: None, tenant_id: UUID,
        usuario_id: UUID, otro_usuario_id: UUID,
    ) -> None:
        """Stats reflejan contadores derivados."""
        aviso_id = await crear_aviso(db_session, tenant_id, requiere_ack=True)

        from app.repositories.acknowledgment_repository import AcknowledgmentRepository

        ack_repo = AcknowledgmentRepository(db_session, tenant_id)
        await ack_repo.confirmar(aviso_id, usuario_id)
        await ack_repo.confirmar(aviso_id, otro_usuario_id)

        from app.services.aviso_service import AvisoService

        service = AvisoService(db_session, tenant_id)
        stats = await service.obtener_stats(aviso_id)
        assert stats["total_acks"] == 2
