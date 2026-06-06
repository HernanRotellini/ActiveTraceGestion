"""Tests para C-13 Encuentros: slots recurrentes, instancias, HTML, vista admin.

Strict TDD: RED → GREEN → TRIANGULATE → REFACTOR.
"""

from datetime import UTC, date, datetime, time
from typing import Any
from uuid import UUID

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
async def encuentro_schema(db_engine: None):
    """Creates full schema for encuentros tests."""
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
# 8.1 — Tests unitarios encuentros
# ═══════════════════════════════════════════════════════════════


class TestSlotRecurrente:
    """8.1.a — Slot recurrente genera N instancias."""

    async def test_slot_recurrente_genera_instancias(
        self, encuentro_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
    ) -> None:
        """RED: crear slot con 4 semanas genera 4 instancias."""
        from app.services.encuentro_service import EncuentroService

        tid = seed_tenant_admin["tenant_id"]
        svc = EncuentroService(db_session, tid, seed_tenant_admin["user_id"])

        result = await svc.crear_slot_recurrente(
            asignacion_id=seed_estructura["asignacion_id"],
            materia_id=seed_estructura["materia_id"],
            titulo="Clase de Matemática",
            dia_semana="Lunes",
            hora=time(18, 0),
            fecha_inicio=date(2026, 6, 1),
            cant_semanas=4,
        )
        assert result["id"] is not None
        assert result["cant_semanas"] == 4
        assert len(result["instancias"]) == 4
        assert result["instancias"][0]["fecha"] == "2026-06-01"
        assert result["instancias"][1]["fecha"] == "2026-06-08"
        assert result["instancias"][2]["fecha"] == "2026-06-15"
        assert result["instancias"][3]["fecha"] == "2026-06-22"

    async def test_todas_las_instancias_programadas(
        self, encuentro_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
    ) -> None:
        """TRIANGULATE: todas las instancias creadas con estado Programado."""
        from app.services.encuentro_service import EncuentroService

        tid = seed_tenant_admin["tenant_id"]
        svc = EncuentroService(db_session, tid, seed_tenant_admin["user_id"])

        result = await svc.crear_slot_recurrente(
            asignacion_id=seed_estructura["asignacion_id"],
            materia_id=seed_estructura["materia_id"],
            titulo="Test",
            dia_semana="Martes",
            hora=time(10, 0),
            fecha_inicio=date(2026, 7, 1),
            cant_semanas=2,
        )
        for inst in result["instancias"]:
            assert inst["estado"] == "Programado"


class TestInstanciaUnica:
    """8.1.b — Instancia única."""

    async def test_crear_instancia_unica(
        self, encuentro_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
    ) -> None:
        """RED: crear instancia sin slot."""
        from app.services.encuentro_service import EncuentroService

        tid = seed_tenant_admin["tenant_id"]
        svc = EncuentroService(db_session, tid, seed_tenant_admin["user_id"])

        result = await svc.crear_instancia_unica(
            materia_id=seed_estructura["materia_id"],
            fecha=date(2026, 7, 15),
            hora=time(10, 0),
            titulo="Consulta pre-parcial",
        )
        assert result["id"] is not None
        assert result["estado"] == "Programado"
        assert result["fecha"] == "2026-07-15"
        assert result["titulo"] == "Consulta pre-parcial"


class TestActualizarInstancia:
    """8.1.c — Edición de instancia sin afectar slot."""

    async def test_actualizar_estado_a_realizado(
        self, encuentro_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
    ) -> None:
        """RED: actualizar instancia a Realizado solo afecta esa instancia."""
        from app.services.encuentro_service import EncuentroService

        tid = seed_tenant_admin["tenant_id"]
        svc = EncuentroService(db_session, tid, seed_tenant_admin["user_id"])

        slot = await svc.crear_slot_recurrente(
            asignacion_id=seed_estructura["asignacion_id"],
            materia_id=seed_estructura["materia_id"],
            titulo="Test",
            dia_semana="Lunes",
            hora=time(18, 0),
            fecha_inicio=date(2026, 6, 1),
            cant_semanas=3,
        )
        instancia_id = slot["instancias"][0]["id"]

        result = await svc.actualizar_instancia(
            instancia_id=instancia_id,
            estado="Realizado",
            video_url="https://zoom.us/rec/abc123",
        )
        assert result["estado"] == "Realizado"
        assert result["video_url"] == "https://zoom.us/rec/abc123"

    async def test_resto_instancias_no_afectadas(
        self, encuentro_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
    ) -> None:
        """TRIANGULATE: otras instancias del mismo slot no se ven afectadas."""
        from app.services.encuentro_service import EncuentroService

        tid = seed_tenant_admin["tenant_id"]
        svc = EncuentroService(db_session, tid, seed_tenant_admin["user_id"])

        slot = await svc.crear_slot_recurrente(
            asignacion_id=seed_estructura["asignacion_id"],
            materia_id=seed_estructura["materia_id"],
            titulo="Test",
            dia_semana="Lunes",
            hora=time(18, 0),
            fecha_inicio=date(2026, 6, 1),
            cant_semanas=2,
        )

        await svc.actualizar_instancia(
            instancia_id=slot["instancias"][0]["id"],
            estado="Realizado",
        )

        instancias = await svc.repo.listar_instancias()
        estados = {str(i.id): i.estado.value for i in instancias}
        assert estados[str(slot["instancias"][0]["id"])] == "Realizado"
        assert estados[str(slot["instancias"][1]["id"])] == "Programado"

    async def test_cancelar_instancia_individual(
        self, encuentro_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
    ) -> None:
        """TRIANGULATE: cancelar instancia individual."""
        from app.services.encuentro_service import EncuentroService

        tid = seed_tenant_admin["tenant_id"]
        svc = EncuentroService(db_session, tid, seed_tenant_admin["user_id"])

        slot = await svc.crear_slot_recurrente(
            asignacion_id=seed_estructura["asignacion_id"],
            materia_id=seed_estructura["materia_id"],
            titulo="Test",
            dia_semana="Lunes",
            hora=time(18, 0),
            fecha_inicio=date(2026, 6, 1),
            cant_semanas=2,
        )

        result = await svc.actualizar_instancia(
            instancia_id=slot["instancias"][0]["id"],
            estado="Cancelado",
        )
        assert result["estado"] == "Cancelado"


class TestHtmlBlock:
    """8.1.d — Generación de HTML block."""

    async def test_generar_html_con_instancias(
        self, encuentro_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
    ) -> None:
        """RED: generar HTML con encuentros."""
        from app.services.encuentro_service import EncuentroService

        tid = seed_tenant_admin["tenant_id"]
        svc = EncuentroService(db_session, tid, seed_tenant_admin["user_id"])

        await svc.crear_slot_recurrente(
            asignacion_id=seed_estructura["asignacion_id"],
            materia_id=seed_estructura["materia_id"],
            titulo="Test",
            dia_semana="Lunes",
            hora=time(18, 0),
            fecha_inicio=date(2026, 6, 1),
            cant_semanas=2,
        )

        html = await svc.generar_html_block(seed_estructura["materia_id"])
        assert "<table" in html
        assert "2026-06-01" in html
        assert "href=" in html

    async def test_html_sin_instancias(
        self, encuentro_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        """TRIANGULATE: HTML sin instancias."""
        from app.services.encuentro_service import EncuentroService

        tid = seed_tenant_admin["tenant_id"]
        svc = EncuentroService(db_session, tid, seed_tenant_admin["user_id"])

        html = await svc.generar_html_block(UUID(int=0))
        assert "No hay encuentros" in html


class TestDiaInvalido:
    """8.1.e — Validación de día inválido."""

    async def test_dia_invalido_rechaza(
        self, encuentro_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
    ) -> None:
        """RED: día inválido rechaza."""
        from app.services.encuentro_service import EncuentroError, EncuentroService

        tid = seed_tenant_admin["tenant_id"]
        svc = EncuentroService(db_session, tid, seed_tenant_admin["user_id"])

        with pytest.raises(EncuentroError, match="Día de semana inválido"):
            await svc.crear_slot_recurrente(
                asignacion_id=seed_estructura["asignacion_id"],
                materia_id=seed_estructura["materia_id"],
                titulo="Test",
                dia_semana="InvalidDay",
                hora=time(18, 0),
                fecha_inicio=date(2026, 6, 1),
                cant_semanas=0,
            )


class TestAdminListar:
    """8.1.f — Vista admin de instancias."""

    async def test_listar_admin_con_filtros(
        self, encuentro_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
    ) -> None:
        """RED: listar admin con filtro materia."""
        from app.services.encuentro_service import EncuentroService

        tid = seed_tenant_admin["tenant_id"]
        svc = EncuentroService(db_session, tid, seed_tenant_admin["user_id"])

        await svc.crear_slot_recurrente(
            asignacion_id=seed_estructura["asignacion_id"],
            materia_id=seed_estructura["materia_id"],
            titulo="Test",
            dia_semana="Lunes",
            hora=time(18, 0),
            fecha_inicio=date(2026, 6, 1),
            cant_semanas=2,
        )

        result = await svc.listar_admin(
            materia_id=seed_estructura["materia_id"],
        )
        assert len(result) >= 1
        assert result[0]["materia_id"] == seed_estructura["materia_id"]

    async def test_listar_admin_con_estado(
        self, encuentro_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
    ) -> None:
        """TRIANGULATE: filtrar admin por estado."""
        from app.services.encuentro_service import EncuentroService

        tid = seed_tenant_admin["tenant_id"]
        svc = EncuentroService(db_session, tid, seed_tenant_admin["user_id"])

        await svc.crear_slot_recurrente(
            asignacion_id=seed_estructura["asignacion_id"],
            materia_id=seed_estructura["materia_id"],
            titulo="Test",
            dia_semana="Lunes",
            hora=time(18, 0),
            fecha_inicio=date(2026, 6, 1),
            cant_semanas=1,
        )

        result = await svc.listar_admin(estado="Programado")
        assert all(r["estado"] == "Programado" for r in result)
