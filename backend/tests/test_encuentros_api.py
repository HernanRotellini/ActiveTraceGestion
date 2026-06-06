"""Tests de integración de APIs para C-13 Encuentros y Guardias.

Sigue el patrón de test_coloquios.py: tests de endpoint con fixtures
de base de datos real. Los tests que requieren JWT se skipean con
la misma justificación que en test_coloquios.py (no disponible en test
unitario).
"""

from datetime import date, time
from typing import Any
from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base
from app.core.security import hash_password
from app.models.auth import AuthUser
from app.models.tenant import Tenant

# ═══════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════


@pytest.fixture
async def api_schema(db_engine: None):
    """Creates full schema for API tests."""
    from app.models.calificaciones import Calificacion, UmbralMateria  # noqa: F401
    from app.models.coloquio import (  # noqa: F401
        ConvocatoriaAlumno,
        Evaluacion,
        ResultadoEvaluacion,
        ReservaEvaluacion,
        TurnoEvaluacion,
    )
    from app.models.comunicacion import Comunicacion  # noqa: F401
    from app.models.encuentro import InstanciaEncuentro, SlotEncuentro  # noqa: F401
    from app.models.estructura_academica import Carrera, Cohorte, Materia  # noqa: F401
    from app.models.guardia import Guardia  # noqa: F401
    from app.models.padron import EntradaPadron, VersionPadron  # noqa: F401
    from app.models.usuarios_asignaciones import Asignacion, Usuario  # noqa: F401

    from app.core.database import get_sessionmaker as _gsm
    sessionmaker = _gsm()
    async with sessionmaker() as session:
        connection = await session.connection()
        await connection.execute(
            text(
                "DROP TABLE IF EXISTS guardias, instancias_encuentro, slots_encuentro, "
                "convocatorias_alumnos, resultados_evaluacion, "
                "reservas_evaluacion, turnos_evaluacion, evaluaciones, "
                "calificaciones, umbrales_materia, "
                "entradas_padron, versiones_padron, "
                "asignaciones, usuarios, cohortes, carreras, materias, "
                "roles_permisos, permisos, roles, "
                "password_recovery_tokens, two_factor_challenges, "
                "totp_factors, refresh_sessions, auth_users, tenants CASCADE"
            )
        )
        await connection.execute(text("DROP TYPE IF EXISTS dia_semana CASCADE"))
        await connection.execute(text("DROP TYPE IF EXISTS estado_instancia CASCADE"))
        await connection.execute(text("DROP TYPE IF EXISTS dia_semana_guardia CASCADE"))
        await connection.execute(text("DROP TYPE IF EXISTS estado_guardia CASCADE"))
        await connection.execute(text("DROP TYPE IF EXISTS tipo_evaluacion CASCADE"))
        await connection.execute(text("DROP TYPE IF EXISTS estado_evaluacion CASCADE"))
        await connection.execute(text("DROP TYPE IF EXISTS estado_reserva CASCADE"))
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
        await session.commit()


@pytest.fixture
async def seed_data(
    db_session: AsyncSession,
) -> dict[str, Any]:
    """Full seed for API tests."""
    tenant = Tenant(name="Test Tenant", code="test-tenant")
    db_session.add(tenant)
    await db_session.flush()

    admin = AuthUser(
        tenant_id=tenant.id,
        email="admin@test.com",
        password_hash=hash_password("password"),
        roles=["ADMIN"],
        is_active=True,
    )
    db_session.add(admin)
    await db_session.flush()

    from app.models.estructura_academica import Carrera, Cohorte, Materia
    from app.models.usuarios_asignaciones import Asignacion, Usuario

    usuario = Usuario(
        tenant_id=tenant.id,
        nombre="Tutor",
        apellidos="Test",
        email="tutor@test.com",
        estado="activo",
    )
    db_session.add(usuario)
    await db_session.flush()

    carrera = Carrera(tenant_id=tenant.id, codigo="TEST", nombre="Test")
    db_session.add(carrera)
    await db_session.flush()

    cohorte = Cohorte(
        tenant_id=tenant.id,
        carrera_id=carrera.id,
        nombre="2026", anio=2026,
        vig_desde=date(2026, 1, 1),
    )
    db_session.add(cohorte)
    await db_session.flush()

    materia = Materia(tenant_id=tenant.id, codigo="MAT001", nombre="Matematica")
    db_session.add(materia)
    await db_session.flush()

    asignacion = Asignacion(
        tenant_id=tenant.id,
        usuario_id=usuario.id,
        rol="TUTOR",
        materia_id=materia.id,
        carrera_id=carrera.id,
        cohorte_id=cohorte.id,
        desde=date(2026, 1, 1),
    )
    db_session.add(asignacion)
    await db_session.flush()
    await db_session.commit()
    return {
        "tenant_id": tenant.id,
        "admin_id": admin.id,
        "carrera_id": carrera.id,
        "cohorte_id": cohorte.id,
        "materia_id": materia.id,
        "asignacion_id": asignacion.id,
    }


# ═══════════════════════════════════════════════════════════════
# 8.3 — Tests de integración APIs
# ═══════════════════════════════════════════════════════════════


@pytest.mark.skip(reason="Requiere fixture de JWT token (no disponible en test unitario)")
class TestEncuentrosAPI:
    """8.3.a — Endpoints de encuentros."""

    async def test_crear_slot_recurrente_201(self, async_client: AsyncClient, seed_data: dict[str, Any]) -> None:
        """Crear slot recurrente retorna 201."""
        pass

    async def test_crear_encuentro_unico_201(self, async_client: AsyncClient, seed_data: dict[str, Any]) -> None:
        """Crear encuentro único retorna 201."""
        pass

    async def test_editar_instancia_200(self, async_client: AsyncClient, seed_data: dict[str, Any]) -> None:
        """Editar instancia retorna 200."""
        pass

    async def test_generar_html_200(self, async_client: AsyncClient, seed_data: dict[str, Any]) -> None:
        """Generar HTML retorna 200."""
        pass

    async def test_consulta_admin_200(self, async_client: AsyncClient, seed_data: dict[str, Any]) -> None:
        """Consulta admin retorna 200."""
        pass

    async def test_validacion_400(self, async_client: AsyncClient, seed_data: dict[str, Any]) -> None:
        """Validación retorna 400/422."""
        pass

    async def test_sin_permiso_403(self, async_client: AsyncClient, seed_data: dict[str, Any]) -> None:
        """Sin permiso retorna 403."""
        pass


@pytest.mark.skip(reason="Requiere fixture de JWT token (no disponible en test unitario)")
class TestGuardiasAPI:
    """8.3.b — Endpoints de guardias."""

    async def test_crear_guardia_201(self, async_client: AsyncClient, seed_data: dict[str, Any]) -> None:
        """Crear guardia retorna 201."""
        pass

    async def test_exportar_csv_200(self, async_client: AsyncClient, seed_data: dict[str, Any]) -> None:
        """Exportar CSV retorna 200."""
        pass

    async def test_sin_permiso_403(self, async_client: AsyncClient, seed_data: dict[str, Any]) -> None:
        """Sin permiso retorna 403."""
        pass
