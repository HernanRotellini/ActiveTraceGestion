"""Tests para C-13 Guardias: registro, consulta filtrada, cambio de estado, CSV.

Strict TDD: RED → GREEN → TRIANGULATE → REFACTOR.
"""

from datetime import date, time
from typing import Any

import pytest
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
async def guardia_schema(db_engine: None):
    """Creates full schema for guardias tests."""
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
async def seed_tenant_admin(db_session: AsyncSession) -> dict[str, Any]:
    """Seeds tenant + admin user."""
    tenant = Tenant(name="Test Tenant", code="test-tenant")
    db_session.add(tenant)
    await db_session.flush()

    user = AuthUser(
        tenant_id=tenant.id,
        email="admin@test.com",
        password_hash=hash_password("password"),
        roles=["ADMIN"],
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.commit()
    return {"tenant_id": tenant.id, "tenant_code": tenant.code, "user_id": user.id}


@pytest.fixture
async def seed_estructura(
    db_session: AsyncSession,
    seed_tenant_admin: dict[str, Any],
) -> dict[str, Any]:
    """Seeds carrera, cohorte, materia, usuario, asignacion."""
    from app.models.estructura_academica import Carrera, Cohorte, Materia
    from app.models.usuarios_asignaciones import Asignacion, Usuario

    tid = seed_tenant_admin["tenant_id"]

    usuario = Usuario(
        tenant_id=tid,
        nombre="Tutor",
        apellidos="Test",
        email="tutor@test.com",
        estado="activo",
    )
    db_session.add(usuario)
    await db_session.flush()

    carrera = Carrera(
        tenant_id=tid, codigo="TEST", nombre="Test",
    )
    db_session.add(carrera)
    await db_session.flush()

    cohorte = Cohorte(
        tenant_id=tid,
        carrera_id=carrera.id,
        nombre="2026", anio=2026,
        vig_desde=date(2026, 1, 1),
    )
    db_session.add(cohorte)
    await db_session.flush()

    materia = Materia(
        tenant_id=tid,
        codigo="MAT001", nombre="Matematica",
    )
    db_session.add(materia)
    await db_session.flush()

    asignacion = Asignacion(
        tenant_id=tid,
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
        "carrera_id": carrera.id, "cohorte_id": cohorte.id,
        "materia_id": materia.id, "asignacion_id": asignacion.id,
        "usuario_id": usuario.id,
    }


# ═══════════════════════════════════════════════════════════════
# 8.2 — Tests unitarios guardias
# ═══════════════════════════════════════════════════════════════


class TestRegistrarGuardia:
    """8.2.a — Registro de guardia."""

    async def test_registrar_guardia_exitosa(
        self, guardia_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
    ) -> None:
        """RED: registrar guardia exitosamente."""
        from app.services.guardia_service import GuardiaService

        tid = seed_tenant_admin["tenant_id"]
        svc = GuardiaService(db_session, tid, seed_tenant_admin["user_id"])

        result = await svc.registrar(
            asignacion_id=seed_estructura["asignacion_id"],
            materia_id=seed_estructura["materia_id"],
            carrera_id=seed_estructura["carrera_id"],
            cohorte_id=seed_estructura["cohorte_id"],
            dia="Lunes",
            horario="14:00-14:45",
        )
        assert result["id"] is not None
        assert result["dia"] == "Lunes"
        assert result["estado"] == "Pendiente"
        assert result["horario"] == "14:00-14:45"

    async def test_registrar_con_estado_personalizado(
        self, guardia_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
    ) -> None:
        """TRIANGULATE: registrar con estado personalizado."""
        from app.services.guardia_service import GuardiaService

        tid = seed_tenant_admin["tenant_id"]
        svc = GuardiaService(db_session, tid, seed_tenant_admin["user_id"])

        result = await svc.registrar(
            asignacion_id=seed_estructura["asignacion_id"],
            materia_id=seed_estructura["materia_id"],
            carrera_id=seed_estructura["carrera_id"],
            cohorte_id=seed_estructura["cohorte_id"],
            dia="Martes",
            horario="15:00-15:45",
            estado="Realizada",
        )
        assert result["estado"] == "Realizada"

    async def test_dia_invalido_rechaza(
        self, guardia_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
    ) -> None:
        """TRIANGULATE: día inválido rechaza."""
        from app.services.guardia_service import GuardiaError, GuardiaService

        tid = seed_tenant_admin["tenant_id"]
        svc = GuardiaService(db_session, tid, seed_tenant_admin["user_id"])

        with pytest.raises(GuardiaError, match="Día de semana inválido"):
            await svc.registrar(
                asignacion_id=seed_estructura["asignacion_id"],
                materia_id=seed_estructura["materia_id"],
                carrera_id=seed_estructura["carrera_id"],
                cohorte_id=seed_estructura["cohorte_id"],
                dia="InvalidDay",
                horario="14:00-14:45",
            )


class TestConsultarGuardias:
    """8.2.b — Consulta filtrada de guardias."""

    async def test_listar_guardias_con_filtro_materia(
        self, guardia_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
    ) -> None:
        """RED: listar guardias filtradas por materia."""
        from app.services.guardia_service import GuardiaService

        tid = seed_tenant_admin["tenant_id"]
        svc = GuardiaService(db_session, tid, seed_tenant_admin["user_id"])

        await svc.registrar(
            asignacion_id=seed_estructura["asignacion_id"],
            materia_id=seed_estructura["materia_id"],
            carrera_id=seed_estructura["carrera_id"],
            cohorte_id=seed_estructura["cohorte_id"],
            dia="Lunes",
            horario="14:00-14:45",
        )

        result = await svc.listar(materia_id=seed_estructura["materia_id"])
        assert len(result) >= 1
        assert result[0]["materia_id"] == seed_estructura["materia_id"]

    async def test_listar_guardias_sin_filtros(
        self, guardia_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
    ) -> None:
        """TRIANGULATE: listar todas las guardias sin filtros."""
        from app.services.guardia_service import GuardiaService

        tid = seed_tenant_admin["tenant_id"]
        svc = GuardiaService(db_session, tid, seed_tenant_admin["user_id"])

        await svc.registrar(
            asignacion_id=seed_estructura["asignacion_id"],
            materia_id=seed_estructura["materia_id"],
            carrera_id=seed_estructura["carrera_id"],
            cohorte_id=seed_estructura["cohorte_id"],
            dia="Lunes",
            horario="14:00-14:45",
        )

        result = await svc.listar()
        assert len(result) >= 1


class TestActualizarEstado:
    """8.2.c — Cambio de estado de guardia."""

    async def test_actualizar_estado_a_realizada(
        self, guardia_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
    ) -> None:
        """RED: actualizar estado de guardia a Realizada."""
        from app.services.guardia_service import GuardiaService

        tid = seed_tenant_admin["tenant_id"]
        svc = GuardiaService(db_session, tid, seed_tenant_admin["user_id"])

        creada = await svc.registrar(
            asignacion_id=seed_estructura["asignacion_id"],
            materia_id=seed_estructura["materia_id"],
            carrera_id=seed_estructura["carrera_id"],
            cohorte_id=seed_estructura["cohorte_id"],
            dia="Lunes",
            horario="14:00-14:45",
        )

        result = await svc.actualizar_estado(
            guardia_id=creada["id"],
            estado="Realizada",
        )
        assert result["estado"] == "Realizada"

    async def test_actualizar_con_comentarios(
        self, guardia_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
    ) -> None:
        """TRIANGULATE: actualizar estado con comentarios."""
        from app.services.guardia_service import GuardiaService

        tid = seed_tenant_admin["tenant_id"]
        svc = GuardiaService(db_session, tid, seed_tenant_admin["user_id"])

        creada = await svc.registrar(
            asignacion_id=seed_estructura["asignacion_id"],
            materia_id=seed_estructura["materia_id"],
            carrera_id=seed_estructura["carrera_id"],
            cohorte_id=seed_estructura["cohorte_id"],
            dia="Lunes",
            horario="14:00-14:45",
        )

        result = await svc.actualizar_estado(
            guardia_id=creada["id"],
            estado="Cancelada",
            comentarios="Se canceló por feriado",
        )
        assert result["estado"] == "Cancelada"
        assert result["comentarios"] == "Se canceló por feriado"


class TestExportarCSV:
    """8.2.d — Exportación CSV de guardias."""

    async def test_exportar_csv_con_datos(
        self, guardia_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
    ) -> None:
        """RED: exportar CSV con guardias."""
        from app.services.guardia_service import GuardiaService

        tid = seed_tenant_admin["tenant_id"]
        svc = GuardiaService(db_session, tid, seed_tenant_admin["user_id"])

        await svc.registrar(
            asignacion_id=seed_estructura["asignacion_id"],
            materia_id=seed_estructura["materia_id"],
            carrera_id=seed_estructura["carrera_id"],
            cohorte_id=seed_estructura["cohorte_id"],
            dia="Lunes",
            horario="14:00-14:45",
        )

        csv_content = await svc.exportar_csv()
        assert "Lunes" in csv_content
        assert "14:00-14:45" in csv_content
        assert csv_content.startswith("\ufeff")

    async def test_exportar_csv_vacio(
        self, guardia_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        """TRIANGULATE: exportar CSV sin datos solo headers."""
        from app.services.guardia_service import GuardiaService

        tid = seed_tenant_admin["tenant_id"]
        svc = GuardiaService(db_session, tid, seed_tenant_admin["user_id"])

        csv_content = await svc.exportar_csv()
        assert "dia" in csv_content
        assert "horario" in csv_content
