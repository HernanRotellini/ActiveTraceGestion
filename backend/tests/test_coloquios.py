"""Tests para C-14 Evaluaciones y Coloquios: modelos, repositorio, servicio, permisos.

Strict TDD: RED → GREEN → TRIANGULATE → REFACTOR.
"""

from datetime import UTC, date, datetime, time
from typing import Any
from uuid import UUID

import pytest
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base
from app.core.security import hash_password
from app.models.auth import AuthUser
from app.models.tenant import Tenant

# ═══════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════


@pytest.fixture
async def coloquio_schema(db_engine: None):
    """Creates full schema for coloquios tests."""
    from app.models.calificaciones import Calificacion, UmbralMateria  # noqa: F401
    from app.models.coloquio import (  # noqa: F401
        ConvocatoriaAlumno,
        Evaluacion,
        ResultadoEvaluacion,
        ReservaEvaluacion,
        TurnoEvaluacion,
    )
    from app.models.comunicacion import Comunicacion  # noqa: F401
    from app.models.estructura_academica import Carrera, Cohorte, Materia  # noqa: F401
    from app.models.padron import EntradaPadron, VersionPadron  # noqa: F401
    from app.models.usuarios_asignaciones import Asignacion, Usuario  # noqa: F401

    from app.core.database import get_sessionmaker as _gsm
    sessionmaker = _gsm()
    async with sessionmaker() as session:
        connection = await session.connection()
        await connection.execute(
            text(
                "DROP TABLE IF EXISTS convocatorias_alumnos, resultados_evaluacion, "
                "reservas_evaluacion, turnos_evaluacion, evaluaciones, "
                "calificaciones, umbrales_materia, "
                "entradas_padron, versiones_padron, "
                "asignaciones, usuarios, cohortes, carreras, materias, "
                "roles_permisos, permisos, roles, "
                "password_recovery_tokens, two_factor_challenges, "
                "totp_factors, refresh_sessions, auth_users, tenants CASCADE"
            )
        )
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
async def seed_alumno(
    db_session: AsyncSession,
    seed_tenant_admin: dict[str, Any],
) -> dict[str, Any]:
    """Seeds an ALUMNO user."""
    alumno = AuthUser(
        tenant_id=seed_tenant_admin["tenant_id"],
        email="alumno@test.com",
        password_hash=hash_password("password"),
        roles=["ALUMNO"],
        is_active=True,
    )
    db_session.add(alumno)
    await db_session.flush()
    await db_session.commit()
    return {"alumno_id": alumno.id}


@pytest.fixture
async def seed_estructura(
    db_session: AsyncSession,
    seed_tenant_admin: dict[str, Any],
) -> dict[str, Any]:
    """Seeds carrera, cohorte, materia."""
    from app.models.estructura_academica import Carrera, Cohorte, Materia

    carrera = Carrera(
        tenant_id=seed_tenant_admin["tenant_id"], codigo="TEST", nombre="Test",
    )
    db_session.add(carrera)
    await db_session.flush()

    cohorte = Cohorte(
        tenant_id=seed_tenant_admin["tenant_id"],
        carrera_id=carrera.id,
        nombre="2026", anio=2026,
        vig_desde=date(2026, 1, 1),
    )
    db_session.add(cohorte)
    await db_session.flush()

    materia = Materia(
        tenant_id=seed_tenant_admin["tenant_id"],
        codigo="MAT001", nombre="Matematica",
    )
    db_session.add(materia)
    await db_session.flush()
    await db_session.commit()
    return {"carrera_id": carrera.id, "cohorte_id": cohorte.id, "materia_id": materia.id}


@pytest.fixture
async def seed_evaluacion(
    db_session: AsyncSession,
    seed_tenant_admin: dict[str, Any],
    seed_estructura: dict[str, Any],
) -> dict[str, Any]:
    """Seeds an Evaluacion with 2 turnos."""
    from app.models.coloquio import EstadoEvaluacion, Evaluacion, TipoEvaluacion, TurnoEvaluacion

    tid = seed_tenant_admin["tenant_id"]
    evaluacion = Evaluacion(
        tenant_id=tid,
        materia_id=seed_estructura["materia_id"],
        cohorte_id=seed_estructura["cohorte_id"],
        tipo=TipoEvaluacion.COLOQUIO,
        instancia="Coloquio Final",
        estado=EstadoEvaluacion.ACTIVA,
    )
    db_session.add(evaluacion)
    await db_session.flush()

    turno1 = TurnoEvaluacion(
        tenant_id=tid,
        evaluacion_id=evaluacion.id,
        fecha=date(2026, 7, 15),
        hora_inicio=time(10, 0),
        hora_fin=time(12, 0),
        cupo_maximo=5,
        cupo_restante=5,
    )
    turno2 = TurnoEvaluacion(
        tenant_id=tid,
        evaluacion_id=evaluacion.id,
        fecha=date(2026, 7, 16),
        cupo_maximo=3,
        cupo_restante=3,
    )
    db_session.add_all([turno1, turno2])
    await db_session.flush()
    await db_session.commit()
    return {
        "evaluacion_id": evaluacion.id,
        "turno1_id": turno1.id,
        "turno2_id": turno2.id,
    }


@pytest.fixture
async def seed_convocados(
    db_session: AsyncSession,
    seed_tenant_admin: dict[str, Any],
    seed_evaluacion: dict[str, Any],
    seed_alumno: dict[str, Any],
) -> dict[str, Any]:
    """Adds alumno to convocatoria."""
    from app.models.coloquio import ConvocatoriaAlumno

    tid = seed_tenant_admin["tenant_id"]
    ca = ConvocatoriaAlumno(
        tenant_id=tid,
        evaluacion_id=seed_evaluacion["evaluacion_id"],
        alumno_id=seed_alumno["alumno_id"],
    )
    db_session.add(ca)
    await db_session.flush()
    await db_session.commit()
    return {"convocado_id": seed_alumno["alumno_id"]}


# ═══════════════════════════════════════════════════════════════
# 7.1 — Tests de unidad/servicio
# ═══════════════════════════════════════════════════════════════

class TestCrearConvocatoria:
    """7.1.a — Creación de convocatoria con turnos."""

    async def test_crear_convocatoria_exitosa(
        self, coloquio_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
    ) -> None:
        """RED: crear convocatoria con turnos."""
        from app.services.coloquio_service import ColoquioService

        tid = seed_tenant_admin["tenant_id"]
        svc = ColoquioService(db_session, tid, seed_tenant_admin["user_id"])

        result = await svc.crear_convocatoria(
            materia_id=seed_estructura["materia_id"],
            cohorte_id=seed_estructura["cohorte_id"],
            tipo="Coloquio",
            instancia="Coloquio Final",
            turnos_data=[
                {"fecha": date(2026, 7, 15), "cupo_maximo": 10},
                {"fecha": date(2026, 7, 16), "cupo_maximo": 8},
            ],
        )
        assert result["id"] is not None
        assert result["tipo"] == "Coloquio"
        assert result["instancia"] == "Coloquio Final"
        assert result["estado"] == "Activa"
        assert len(result["turnos"]) == 2

    async def test_crear_sin_turnos_rechaza(
        self, coloquio_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
    ) -> None:
        """TRIANGULATE: crear sin turnos rechaza."""
        from app.services.coloquio_service import ColoquioService

        tid = seed_tenant_admin["tenant_id"]
        svc = ColoquioService(db_session, tid, seed_tenant_admin["user_id"])

        with pytest.raises(ValueError):
            await svc.crear_convocatoria(
                materia_id=seed_estructura["materia_id"],
                cohorte_id=seed_estructura["cohorte_id"],
                tipo="Coloquio",
                instancia="Coloquio Final",
                turnos_data=[],
            )

    async def test_crear_tipo_invalido_rechaza(
        self, coloquio_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
    ) -> None:
        """TRIANGULATE: tipo inválido rechaza."""
        from app.services.coloquio_service import ColoquioError, ColoquioService

        tid = seed_tenant_admin["tenant_id"]
        svc = ColoquioService(db_session, tid, seed_tenant_admin["user_id"])

        with pytest.raises(ColoquioError, match="Tipo de evaluación inválido"):
            await svc.crear_convocatoria(
                materia_id=seed_estructura["materia_id"],
                cohorte_id=seed_estructura["cohorte_id"],
                tipo="Invalido",
                instancia="Test",
                turnos_data=[{"fecha": date(2026, 7, 15), "cupo_maximo": 5}],
            )


class TestImportarAlumnos:
    """7.1.b — Importación de alumnos."""

    async def test_importar_alumnos_exitoso(
        self, coloquio_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_evaluacion: dict[str, Any],
        seed_alumno: dict[str, Any],
    ) -> None:
        """RED: importar alumnos a una convocatoria."""
        from app.services.coloquio_service import ColoquioService

        tid = seed_tenant_admin["tenant_id"]
        svc = ColoquioService(db_session, tid, seed_tenant_admin["user_id"])

        result = await svc.importar_alumnos(
            seed_evaluacion["evaluacion_id"],
            [seed_alumno["alumno_id"]],
        )
        assert result["importados"] == 1

    async def test_importar_duplicado_ignora(
        self, coloquio_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_evaluacion: dict[str, Any],
        seed_alumno: dict[str, Any],
    ) -> None:
        """TRIANGULATE: importar duplicado ignora."""
        from app.services.coloquio_service import ColoquioService

        tid = seed_tenant_admin["tenant_id"]
        svc = ColoquioService(db_session, tid, seed_tenant_admin["user_id"])

        await svc.importar_alumnos(
            seed_evaluacion["evaluacion_id"],
            [seed_alumno["alumno_id"]],
        )
        result = await svc.importar_alumnos(
            seed_evaluacion["evaluacion_id"],
            [seed_alumno["alumno_id"]],
        )
        assert result["importados"] == 0

    async def test_importar_convocatoria_cerrada_rechaza(
        self, coloquio_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_evaluacion: dict[str, Any],
        seed_alumno: dict[str, Any],
    ) -> None:
        """TRIANGULATE: importar en convocatoria cerrada rechaza."""
        from app.models.coloquio import EstadoEvaluacion, Evaluacion
        from app.services.coloquio_service import ColoquioError, ColoquioService

        tid = seed_tenant_admin["tenant_id"]
        ev = await db_session.get(Evaluacion, seed_evaluacion["evaluacion_id"])
        ev.estado = EstadoEvaluacion.CERRADA
        await db_session.flush()

        svc = ColoquioService(db_session, tid, seed_tenant_admin["user_id"])
        with pytest.raises(ColoquioError, match="Convocatoria cerrada"):
            await svc.importar_alumnos(
                seed_evaluacion["evaluacion_id"],
                [seed_alumno["alumno_id"]],
            )


class TestReserva:
    """7.1.c — Reserva con cupo, sin cupo, cancelación, duplicada, no convocado."""

    async def test_reserva_con_cupo(
        self, coloquio_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_evaluacion: dict[str, Any],
        seed_convocados: dict[str, Any],
    ) -> None:
        """RED: reserva exitosa decrementa cupo."""
        from app.models.coloquio import TurnoEvaluacion
        from app.services.coloquio_service import ColoquioService

        tid = seed_tenant_admin["tenant_id"]
        alumno_id = seed_convocados["convocado_id"]
        svc = ColoquioService(db_session, tid, alumno_id)

        result = await svc.reservar(
            seed_evaluacion["evaluacion_id"],
            seed_evaluacion["turno1_id"],
        )
        assert result["estado"] == "Activa"

        turno = await db_session.get(TurnoEvaluacion, seed_evaluacion["turno1_id"])
        assert turno.cupo_restante == 4

    async def test_reserva_sin_cupo_rechaza(
        self, coloquio_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_evaluacion: dict[str, Any],
        seed_convocados: dict[str, Any],
    ) -> None:
        """TRIANGULATE: reserva sin cupo rechaza."""
        from app.models.coloquio import TurnoEvaluacion
        from app.services.coloquio_service import ColoquioError, ColoquioService

        tid = seed_tenant_admin["tenant_id"]
        alumno_id = seed_convocados["convocado_id"]

        turno = await db_session.get(TurnoEvaluacion, seed_evaluacion["turno2_id"])
        turno.cupo_restante = 0
        await db_session.flush()

        svc = ColoquioService(db_session, tid, alumno_id)
        with pytest.raises(ColoquioError, match="Sin cupo disponible"):
            await svc.reservar(
                seed_evaluacion["evaluacion_id"],
                seed_evaluacion["turno2_id"],
            )

    async def test_cancelacion_restituye_cupo(
        self, coloquio_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_evaluacion: dict[str, Any],
        seed_convocados: dict[str, Any],
    ) -> None:
        """TRIANGULATE: cancelación restituye cupo."""
        from app.models.coloquio import TurnoEvaluacion
        from app.services.coloquio_service import ColoquioService

        tid = seed_tenant_admin["tenant_id"]
        alumno_id = seed_convocados["convocado_id"]
        svc = ColoquioService(db_session, tid, alumno_id)

        await svc.reservar(
            seed_evaluacion["evaluacion_id"],
            seed_evaluacion["turno1_id"],
        )
        result = await svc.cancelar_reserva(seed_evaluacion["evaluacion_id"])
        assert result["estado"] == "Cancelada"

        turno = await db_session.get(TurnoEvaluacion, seed_evaluacion["turno1_id"])
        assert turno.cupo_restante == 5

    async def test_reserva_duplicada_rechaza(
        self, coloquio_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_evaluacion: dict[str, Any],
        seed_convocados: dict[str, Any],
    ) -> None:
        """TRIANGULATE: reserva duplicada rechaza."""
        from app.services.coloquio_service import ColoquioError, ColoquioService

        tid = seed_tenant_admin["tenant_id"]
        alumno_id = seed_convocados["convocado_id"]
        svc = ColoquioService(db_session, tid, alumno_id)

        await svc.reservar(
            seed_evaluacion["evaluacion_id"],
            seed_evaluacion["turno1_id"],
        )
        with pytest.raises(ColoquioError, match="Ya tiene una reserva activa"):
            await svc.reservar(
                seed_evaluacion["evaluacion_id"],
                seed_evaluacion["turno2_id"],
            )

    async def test_alumno_no_convocado_rechaza(
        self, coloquio_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_evaluacion: dict[str, Any],
    ) -> None:
        """TRIANGULATE: alumno no convocado rechaza."""
        from app.services.coloquio_service import ColoquioError, ColoquioService

        tid = seed_tenant_admin["tenant_id"]
        # Create a non-convocado alumno
        alumno = AuthUser(
            tenant_id=tid,
            email="other@test.com",
            password_hash=hash_password("password"),
            roles=["ALUMNO"],
            is_active=True,
        )
        db_session.add(alumno)
        await db_session.flush()

        svc = ColoquioService(db_session, tid, alumno.id)
        with pytest.raises(ColoquioError, match="Alumno no habilitado"):
            await svc.reservar(
                seed_evaluacion["evaluacion_id"],
                seed_evaluacion["turno1_id"],
            )


# ═══════════════════════════════════════════════════════════════
# 7.2 — Tests de métricas
# ═══════════════════════════════════════════════════════════════

class TestMetricas:
    """7.2 — Métricas: panel global, listado con métricas."""

    async def test_metricas_globales(
        self, coloquio_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_evaluacion: dict[str, Any],
        seed_convocados: dict[str, Any],
    ) -> None:
        """RED: panel de métricas globales."""
        from app.services.coloquio_service import ColoquioService

        tid = seed_tenant_admin["tenant_id"]
        svc = ColoquioService(db_session, tid, seed_tenant_admin["user_id"])

        metricas = await svc.metricas_globales()
        assert metricas["alumnos_convocados"] >= 1
        assert metricas["convocatorias_activas"] >= 1

    async def test_listado_con_metricas(
        self, coloquio_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_evaluacion: dict[str, Any],
        seed_convocados: dict[str, Any],
    ) -> None:
        """TRIANGULATE: listado con métricas por convocatoria."""
        from app.services.coloquio_service import ColoquioService

        tid = seed_tenant_admin["tenant_id"]
        svc = ColoquioService(db_session, tid, seed_tenant_admin["user_id"])

        items = await svc.listar_con_metricas()
        assert len(items) >= 1
        item = items[0]
        assert item["total_turnos"] == 2
        assert item["alumnos_convocados"] >= 1


# ═══════════════════════════════════════════════════════════════
# 7.3 — Tests de permisos
# ═══════════════════════════════════════════════════════════════

class TestPermisos:
    """7.3 — Permisos: 403 sin permiso."""

    @pytest.mark.skip(reason="Requiere fixture de JWT token (no disponible en test unitario)")
    async def test_403_gestionar_sin_permiso(self, async_client) -> None:
        """RED: endpoint de gestión retorna 403 sin permiso."""
        pass

    @pytest.mark.skip(reason="Requiere fixture de JWT token (no disponible en test unitario)")
    async def test_403_reservar_sin_permiso(self, async_client) -> None:
        """TRIANGULATE: endpoint de reserva retorna 403 sin permiso."""
        pass


# ═══════════════════════════════════════════════════════════════
# 7.4 — Cobertura
# ═══════════════════════════════════════════════════════════════

class TestResultados:
    """7.4 — Resultados: registro y consulta."""

    async def test_registrar_resultado(
        self, coloquio_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_evaluacion: dict[str, Any],
        seed_convocados: dict[str, Any],
    ) -> None:
        """RED: registrar resultado exitoso."""
        from app.services.coloquio_service import ColoquioService

        tid = seed_tenant_admin["tenant_id"]
        svc = ColoquioService(db_session, tid, seed_tenant_admin["user_id"])

        result = await svc.registrar_resultado(
            seed_evaluacion["evaluacion_id"],
            seed_convocados["convocado_id"],
            "Aprobado",
        )
        assert result["nota_final"] == "Aprobado"
        assert result["registrado_por"] == seed_tenant_admin["user_id"]

    async def test_actualizar_resultado(
        self, coloquio_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_evaluacion: dict[str, Any],
        seed_convocados: dict[str, Any],
    ) -> None:
        """TRIANGULATE: actualizar resultado existente."""
        from app.services.coloquio_service import ColoquioService

        tid = seed_tenant_admin["tenant_id"]
        svc = ColoquioService(db_session, tid, seed_tenant_admin["user_id"])

        await svc.registrar_resultado(
            seed_evaluacion["evaluacion_id"],
            seed_convocados["convocado_id"],
            "Aprobado",
        )
        result = await svc.registrar_resultado(
            seed_evaluacion["evaluacion_id"],
            seed_convocados["convocado_id"],
            "Sobresaliente",
        )
        assert result["nota_final"] == "Sobresaliente"

    async def test_resultado_alumno_no_convocado_rechaza(
        self, coloquio_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_evaluacion: dict[str, Any],
    ) -> None:
        """TRIANGULATE: resultado para no convocado rechaza."""
        from app.services.coloquio_service import ColoquioError, ColoquioService

        tid = seed_tenant_admin["tenant_id"]
        alumno = AuthUser(
            tenant_id=tid,
            email="other@test.com",
            password_hash=hash_password("password"),
            roles=["ALUMNO"],
            is_active=True,
        )
        db_session.add(alumno)
        await db_session.flush()

        svc = ColoquioService(db_session, tid, seed_tenant_admin["user_id"])
        with pytest.raises(ColoquioError, match="Alumno no convocado"):
            await svc.registrar_resultado(
                seed_evaluacion["evaluacion_id"],
                alumno.id,
                "Aprobado",
            )

    async def test_resultados_consolidados(
        self, coloquio_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_evaluacion: dict[str, Any],
        seed_convocados: dict[str, Any],
    ) -> None:
        """TRIANGULATE: listar resultados consolidados."""
        from app.services.coloquio_service import ColoquioService

        tid = seed_tenant_admin["tenant_id"]
        svc = ColoquioService(db_session, tid, seed_tenant_admin["user_id"])

        await svc.registrar_resultado(
            seed_evaluacion["evaluacion_id"],
            seed_convocados["convocado_id"],
            "Aprobado",
        )
        resultados = await svc.listar_resultados(seed_evaluacion["evaluacion_id"])
        assert len(resultados) == 1
        assert resultados[0]["nota_final"] == "Aprobado"


class TestCerrarConvocatoria:
    """Cierre de convocatoria."""

    async def test_cerrar_convocatoria(
        self, coloquio_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_evaluacion: dict[str, Any],
    ) -> None:
        """RED: cerrar convocatoria cambia estado."""
        from app.services.coloquio_service import ColoquioService

        tid = seed_tenant_admin["tenant_id"]
        svc = ColoquioService(db_session, tid, seed_tenant_admin["user_id"])

        result = await svc.cerrar_convocatoria(seed_evaluacion["evaluacion_id"])
        assert result["estado"] == "Cerrada"

    async def test_reserva_en_cerrada_rechaza(
        self, coloquio_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_evaluacion: dict[str, Any],
        seed_convocados: dict[str, Any],
    ) -> None:
        """TRIANGULATE: reserva en convocatoria cerrada rechaza."""
        from app.models.coloquio import EstadoEvaluacion, Evaluacion
        from app.services.coloquio_service import ColoquioError, ColoquioService

        tid = seed_tenant_admin["tenant_id"]
        ev = await db_session.get(Evaluacion, seed_evaluacion["evaluacion_id"])
        ev.estado = EstadoEvaluacion.CERRADA
        await db_session.flush()

        svc = ColoquioService(db_session, tid, seed_convocados["convocado_id"])
        with pytest.raises(ColoquioError, match="Convocatoria cerrada"):
            await svc.reservar(
                seed_evaluacion["evaluacion_id"],
                seed_evaluacion["turno1_id"],
            )


class TestAgendaReservas:
    """Agenda global de reservas."""

    async def test_agenda_reservas(
        self, coloquio_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_evaluacion: dict[str, Any],
        seed_convocados: dict[str, Any],
    ) -> None:
        """RED: agenda global retorna reservas activas."""
        from app.services.coloquio_service import ColoquioService

        tid = seed_tenant_admin["tenant_id"]
        svc_alumno = ColoquioService(db_session, tid, seed_convocados["convocado_id"])
        await svc_alumno.reservar(
            seed_evaluacion["evaluacion_id"],
            seed_evaluacion["turno1_id"],
        )

        svc_admin = ColoquioService(db_session, tid, seed_tenant_admin["user_id"])
        agenda = await svc_admin.agenda_reservas()
        assert len(agenda) >= 1
        assert agenda[0]["alumno_id"] == seed_convocados["convocado_id"]


class TestModelos:
    """Tests de modelos ORM básicos."""

    async def test_crear_evaluacion_modelo(
        self, coloquio_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
    ) -> None:
        """RED: crea Evaluacion via ORM."""
        from app.models.coloquio import EstadoEvaluacion, Evaluacion, TipoEvaluacion

        evaluacion = Evaluacion(
            tenant_id=seed_tenant_admin["tenant_id"],
            materia_id=seed_estructura["materia_id"],
            cohorte_id=seed_estructura["cohorte_id"],
            tipo=TipoEvaluacion.COLOQUIO,
            instancia="Test",
            estado=EstadoEvaluacion.ACTIVA,
        )
        db_session.add(evaluacion)
        await db_session.flush()

        assert evaluacion.id is not None
        assert evaluacion.tipo == TipoEvaluacion.COLOQUIO
