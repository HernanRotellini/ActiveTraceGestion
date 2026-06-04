"""Tests para C-11 Análisis: atrasados, ranking, reportes, monitores.

Strict TDD: RED → GREEN → TRIANGULATE → REFACTOR.
"""

from datetime import UTC, date, datetime
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
# Fixtures (same pattern as test_calificaciones.py)
# ═══════════════════════════════════════════════════════════════

@pytest.fixture
async def analisis_schema(db_engine: None):
    """Creates full schema for analysis tests."""
    from app.core.database import get_sessionmaker
    from app.models.calificaciones import Calificacion, UmbralMateria  # noqa: F401
    from app.models.estructura_academica import Carrera, Cohorte, Materia  # noqa: F401
    from app.models.padron import EntradaPadron, VersionPadron  # noqa: F401
    from app.models.usuarios_asignaciones import Asignacion, Usuario  # noqa: F401

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        connection = await session.connection()
        await connection.execute(
            text(
                "DROP TABLE IF EXISTS calificaciones, umbrales_materia, "
                "entradas_padron, versiones_padron, "
                "asignaciones, usuarios, cohortes, carreras, materias, "
                "roles_permisos, permisos, roles, "
                "password_recovery_tokens, two_factor_challenges, "
                "totp_factors, refresh_sessions, auth_users, tenants CASCADE"
            )
        )
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
    db_session: AsyncSession, seed_tenant_admin: dict[str, Any]
) -> dict[str, Any]:
    """Seeds carrera, cohorte, materia."""
    from app.models.estructura_academica import Carrera, Cohorte, Materia

    carrera = Carrera(tenant_id=seed_tenant_admin["tenant_id"], codigo="TEST", nombre="Test")
    db_session.add(carrera)
    await db_session.flush()

    cohorte = Cohorte(
        tenant_id=seed_tenant_admin["tenant_id"],
        carrera_id=carrera.id,
        nombre="2026",
        anio=2026,
        vig_desde=date(2026, 1, 1),
    )
    db_session.add(cohorte)
    await db_session.flush()

    materia = Materia(tenant_id=seed_tenant_admin["tenant_id"], codigo="MAT001", nombre="Matematica")
    db_session.add(materia)
    await db_session.flush()
    await db_session.commit()
    return {"carrera_id": carrera.id, "cohorte_id": cohorte.id, "materia_id": materia.id}


@pytest.fixture
async def seed_padron_activo(
    db_session: AsyncSession,
    seed_tenant_admin: dict[str, Any],
    seed_estructura: dict[str, Any],
) -> dict[str, Any]:
    """Seeds an active padron version with 3 students."""
    from app.models.padron import EntradaPadron, VersionPadron
    from app.models.usuarios_asignaciones import Usuario

    docente = Usuario(
        tenant_id=seed_tenant_admin["tenant_id"],
        nombre="Admin",
        apellidos="Test",
        email="admin.docente@test.com",
    )
    db_session.add(docente)
    await db_session.flush()

    version = VersionPadron(
        tenant_id=seed_tenant_admin["tenant_id"],
        materia_id=seed_estructura["materia_id"],
        cohorte_id=seed_estructura["cohorte_id"],
        cargado_por=docente.id,
        activa=True,
    )
    db_session.add(version)
    await db_session.flush()

    alumno1 = EntradaPadron(
        tenant_id=seed_tenant_admin["tenant_id"],
        version_id=version.id,
        nombre="Juan",
        apellidos="Perez",
        email="juan@test.com",
        comision="A",
        regional="Norte",
    )
    db_session.add(alumno1)
    alumno2 = EntradaPadron(
        tenant_id=seed_tenant_admin["tenant_id"],
        version_id=version.id,
        nombre="Maria",
        apellidos="Gomez",
        email="maria@test.com",
        comision="A",
        regional="Norte",
    )
    db_session.add(alumno2)
    alumno3 = EntradaPadron(
        tenant_id=seed_tenant_admin["tenant_id"],
        version_id=version.id,
        nombre="Carlos",
        apellidos="Lopez",
        email="carlos@test.com",
        comision="B",
        regional="Sur",
    )
    db_session.add(alumno3)
    await db_session.flush()
    await db_session.commit()

    return {
        "version_id": version.id,
        "alumno1_id": alumno1.id,
        "alumno2_id": alumno2.id,
        "alumno3_id": alumno3.id,
    }


@pytest.fixture
async def seed_calificaciones(
    db_session: AsyncSession,
    seed_tenant_admin: dict[str, Any],
    seed_estructura: dict[str, Any],
    seed_padron_activo: dict[str, Any],
) -> dict[str, Any]:
    """Seeds Calificacion records for analysis testing.

    - Juan (alumno1): TP1=75 (aprobado), TP2=Satisfactorio (aprobado textual), TP3 missing
    - Maria (alumno2): TP1=45 (no aprobado), TP2=30 (no aprobado)
    - Carlos (alumno3): no calificaciones at all
    """
    from app.models.calificaciones import Calificacion, OrigenCalificacion

    now = datetime.now(UTC)
    tid = seed_tenant_admin["tenant_id"]
    mid = seed_estructura["materia_id"]

    califs = [
        Calificacion(
            tenant_id=tid, entrada_padron_id=seed_padron_activo["alumno1_id"],
            materia_id=mid, actividad="TP1", nota_numerica=75.0, nota_textual=None,
            aprobado=True, origen=OrigenCalificacion.IMPORTADO, importado_at=now,
        ),
        Calificacion(
            tenant_id=tid, entrada_padron_id=seed_padron_activo["alumno1_id"],
            materia_id=mid, actividad="TP2", nota_numerica=None, nota_textual="Satisfactorio",
            aprobado=True, origen=OrigenCalificacion.IMPORTADO, importado_at=now,
        ),
        Calificacion(
            tenant_id=tid, entrada_padron_id=seed_padron_activo["alumno2_id"],
            materia_id=mid, actividad="TP1", nota_numerica=45.0, nota_textual=None,
            aprobado=False, origen=OrigenCalificacion.IMPORTADO, importado_at=now,
        ),
        Calificacion(
            tenant_id=tid, entrada_padron_id=seed_padron_activo["alumno2_id"],
            materia_id=mid, actividad="TP2", nota_numerica=30.0, nota_textual=None,
            aprobado=False, origen=OrigenCalificacion.IMPORTADO, importado_at=now,
        ),
    ]
    for c in califs:
        db_session.add(c)
    await db_session.flush()
    await db_session.commit()

    return {
        "calif_tp1_juan": califs[0].id,
        "calif_tp2_juan": califs[1].id,
        "calif_tp1_maria": califs[2].id,
        "calif_tp2_maria": califs[3].id,
    }


# ═══════════════════════════════════════════════════════════════
# 2.1 — listar_atrasados
# ═══════════════════════════════════════════════════════════════

class TestListarAtrasados:
    """RED: AnalisisRepository.listar_atrasados no existe aún."""

    async def test_alumno_atrasado_por_actividad_faltante(
        self, analisis_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
        seed_calificaciones: dict[str, Any],
    ) -> None:
        """RED 2.1: alumno sin calificaciones aparece como atrasado (falta)."""
        from app.repositories.analisis import AnalisisRepository

        tid = seed_tenant_admin["tenant_id"]
        repo = AnalisisRepository(db_session, tid)
        materia_id = seed_estructura["materia_id"]

        resultado = await repo.listar_atrasados(materia_id)

        # Carlos (Lopez) has NO calificaciones → atrasado por "falta" en todas las actividades
        carlos_entry = next((r for r in resultado if "Lopez" in r.get("alumno_nombre", "")), None)
        assert carlos_entry is not None, "Carlos sin calificaciones debe aparecer en atrasados"
        assert len(carlos_entry["actividades_atrasadas"]) >= 2, "Carlos debe tener al menos 2 actividades atrasadas"
        for act in carlos_entry["actividades_atrasadas"]:
            assert act["motivo"] in ("falta", "faltante")

    async def test_alumno_atrasado_por_nota_insuficiente(
        self, analisis_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
        seed_calificaciones: dict[str, Any],
    ) -> None:
        """RED 2.1: alumno con nota < umbral aparece en atrasados."""
        from app.repositories.analisis import AnalisisRepository

        tid = seed_tenant_admin["tenant_id"]
        repo = AnalisisRepository(db_session, tid)
        materia_id = seed_estructura["materia_id"]

        resultado = await repo.listar_atrasados(materia_id)

        # Maria: TP1=45 (nota insuficiente contra umbral 60)
        maria_entry = next((r for r in resultado if "Gomez" in r.get("alumno_nombre", "")), None)
        assert maria_entry is not None, "Maria debe aparecer en atrasados"
        tp1_act = next((a for a in maria_entry["actividades_atrasadas"] if a["actividad"] == "TP1"), None)
        assert tp1_act is not None, "TP1 debe estar como actividad atrasada"
        assert tp1_act["motivo"] in ("nota_insuficiente", "nota insuficiente")

    async def test_alumno_con_todo_aprobado_no_aparece(
        self, analisis_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
        seed_calificaciones: dict[str, Any],
    ) -> None:
        """TRIANGULATE: alumno con TP1 y TP2 aprobados pero con TP3 faltante
        SÍ aparece — solo si NO tiene atrasos no aparece.
        Juan sí aparece porque tiene TP3 faltante.
        Como no hay alumno sin atrasos en la data base, forzamos un escenario
        agregando a un alumno4 con todas las actividades cubiertas."""
        from app.models.calificaciones import Calificacion, OrigenCalificacion
        from app.repositories.analisis import AnalisisRepository

        tid = seed_tenant_admin["tenant_id"]
        repo = AnalisisRepository(db_session, tid)
        materia_id = seed_estructura["materia_id"]

        # Add TP3 calificacion for Juan to make him fully approved
        calif_extra = Calificacion(
            tenant_id=tid, entrada_padron_id=seed_padron_activo["alumno1_id"],
            materia_id=materia_id, actividad="TP3", nota_numerica=80.0,
            nota_textual=None, aprobado=True,
            origen=OrigenCalificacion.IMPORTADO, importado_at=datetime.now(UTC),
        )
        db_session.add(calif_extra)
        await db_session.flush()
        await db_session.commit()

        resultado = await repo.listar_atrasados(materia_id)

        # Juan now has all approved — should not appear
        juan_entry = next((r for r in resultado if "Perez" in r.get("alumno_nombre", "")), None)
        assert juan_entry is None, "Juan con todas las actividades aprobadas NO debe aparecer en atrasados"

    async def test_sin_actividades_importadas_retorna_vacio(
        self, analisis_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
    ) -> None:
        """TRIANGULATE: materia sin calificaciones → lista vacía."""
        from app.repositories.analisis import AnalisisRepository

        tid = seed_tenant_admin["tenant_id"]
        repo = AnalisisRepository(db_session, tid)
        materia_id = seed_estructura["materia_id"]

        resultado = await repo.listar_atrasados(materia_id)
        assert resultado == [], "Sin calificaciones debe retornar lista vacía"

    async def test_alumno_sin_usuario_id_en_padron(
        self, analisis_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
    ) -> None:
        """TRIANGULATE: entrada padron sin usuario_id se procesa igual."""
        from app.repositories.analisis import AnalisisRepository

        tid = seed_tenant_admin["tenant_id"]
        repo = AnalisisRepository(db_session, tid)
        materia_id = seed_estructura["materia_id"]

        resultado = await repo.listar_atrasados(materia_id)
        # All students should be properly listed by name
        nombres = [r["alumno_nombre"] for r in resultado]
        assert any("Perez" in n for n in nombres)
        assert any("Gomez" in n for n in nombres)

    async def test_aislamiento_por_materia(
        self, analisis_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
        seed_calificaciones: dict[str, Any],
    ) -> None:
        """TRIANGULATE: query para materia A no incluye datos de materia B."""
        from app.models.estructura_academica import Materia
        from app.models.padron import EntradaPadron, VersionPadron
        from app.models.usuarios_asignaciones import Usuario
        from app.repositories.analisis import AnalisisRepository

        tid = seed_tenant_admin["tenant_id"]
        repo = AnalisisRepository(db_session, tid)
        materia_a = seed_estructura["materia_id"]

        # Crear materia B con su propio padrón
        materia_b = Materia(tenant_id=tid, codigo="MAT002", nombre="Fisica")
        db_session.add(materia_b)
        await db_session.flush()

        version_b = VersionPadron(
            tenant_id=tid, materia_id=materia_b.id,
            cohorte_id=seed_estructura["cohorte_id"],
            cargado_por=seed_padron_activo.get("docente_id", tid),
            activa=True,
        )
        db_session.add(version_b)
        await db_session.flush()

        entrada_b = EntradaPadron(
            tenant_id=tid, version_id=version_b.id,
            nombre="Extra", apellidos="Student", email="extra@test.com",
            comision="X",
        )
        db_session.add(entrada_b)
        await db_session.flush()
        await db_session.commit()

        resultado_a = await repo.listar_atrasados(materia_a)
        resultado_b = await repo.listar_atrasados(materia_b)

        # Materia A has Juan and Maria atrasados
        assert len(resultado_a) >= 2
        # Materia B has no calificaciones → empty
        assert resultado_b == []


# ═══════════════════════════════════════════════════════════════
# 2.2 — ranking_aprobados
# ═══════════════════════════════════════════════════════════════

class TestRankingAprobados:
    """RED: AnalisisRepository.ranking_aprobados no existe aún."""

    async def test_ranking_excluye_sin_aprobadas(
        self, analisis_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
        seed_calificaciones: dict[str, Any],
    ) -> None:
        """RED 2.2: RN-09 excluye alumnos sin aprobadas."""
        from app.repositories.analisis import AnalisisRepository

        tid = seed_tenant_admin["tenant_id"]
        repo = AnalisisRepository(db_session, tid)
        materia_id = seed_estructura["materia_id"]

        resultado = await repo.ranking_aprobados(materia_id)

        # Juan: 2 aprobadas → debe aparecer
        juan = next((r for r in resultado if "Perez" in r.get("alumno_nombre", "")), None)
        assert juan is not None
        assert juan["actividades_aprobadas"] >= 2

        # Carlos: 0 aprobadas → NO debe aparecer (RN-09)
        carlos = next((r for r in resultado if "Lopez" in r.get("alumno_nombre", "")), None)
        assert carlos is None, "Carlos sin aprobadas debe ser excluido (RN-09)"

    async def test_ranking_orden_descendente(
        self, analisis_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
        seed_calificaciones: dict[str, Any],
    ) -> None:
        """TRIANGULATE: ranking ordenado descendente por count."""
        from app.repositories.analisis import AnalisisRepository

        tid = seed_tenant_admin["tenant_id"]
        repo = AnalisisRepository(db_session, tid)
        materia_id = seed_estructura["materia_id"]

        resultado = await repo.ranking_aprobados(materia_id)

        if len(resultado) >= 2:
            for i in range(len(resultado) - 1):
                assert resultado[i]["actividades_aprobadas"] >= resultado[i + 1]["actividades_aprobadas"]

    async def test_ranking_with_tie_sorted_alphabetically(
        self, analisis_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
    ) -> None:
        """TRIANGULATE: empate ordena alfabéticamente (apellido, nombre)."""
        from app.models.calificaciones import Calificacion, OrigenCalificacion
        from app.models.padron import EntradaPadron
        from app.repositories.analisis import AnalisisRepository

        tid = seed_tenant_admin["tenant_id"]
        repo = AnalisisRepository(db_session, tid)
        materia_id = seed_estructura["materia_id"]

        # Give Maria (Gomez) one approved activity so she ties with Juan
        # Actually Juan has 2, Maria has 0 approved. Let me add an approved
        # calificacion for Maria to tie at 1-1 with someone.
        # Better approach: add 2 more students with 1 approved each
        version_id = seed_padron_activo["version_id"]

        for nombre, apellidos in [("Ana", "Alvarez"), ("Beatriz", "Zeta")]:
            entrada = EntradaPadron(
                tenant_id=tid, version_id=version_id,
                nombre=nombre, apellidos=apellidos,
                email=f"{nombre.lower()}@test.com", comision="A",
            )
            db_session.add(entrada)
            await db_session.flush()
            calif = Calificacion(
                tenant_id=tid, entrada_padron_id=entrada.id,
                materia_id=materia_id, actividad="TP1", nota_numerica=80.0,
                nota_textual=None, aprobado=True,
                origen=OrigenCalificacion.IMPORTADO, importado_at=datetime.now(UTC),
            )
            db_session.add(calif)
        await db_session.flush()
        await db_session.commit()

        resultado = await repo.ranking_aprobados(materia_id)
        # Students with 1 approved: Alvarez and Zeta should be alphabetical
        ones = [r for r in resultado if r["actividades_aprobadas"] == 1]
        if len(ones) >= 2:
            assert ones[0]["alumno_nombre"] <= ones[1]["alumno_nombre"]

    async def test_ranking_empty_when_no_approved(
        self, analisis_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
    ) -> None:
        """TRIANGULATE: sin aprobadas → ranking vacío."""
        from app.repositories.analisis import AnalisisRepository

        tid = seed_tenant_admin["tenant_id"]
        repo = AnalisisRepository(db_session, tid)
        otra_materia_id = seed_estructura.get("materia_id")
        # Create materia with no calificaciones

        from app.models.estructura_academica import Materia

        materia_sin = Materia(tenant_id=tid, codigo="MAT-SIN", nombre="Sin Datos")
        db_session.add(materia_sin)
        await db_session.flush()
        await db_session.commit()

        resultado = await repo.ranking_aprobados(materia_sin.id)
        assert resultado == []


# ═══════════════════════════════════════════════════════════════
# 2.3 — reportes_rapidos
# ═══════════════════════════════════════════════════════════════

class TestReportesRapidos:
    """RED: AnalisisRepository.reportes_rapidos no existe aún."""

    async def test_reportes_returns_metrics(
        self, analisis_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
        seed_calificaciones: dict[str, Any],
    ) -> None:
        """RED 2.3: reporte devuelve métricas consolidadas."""
        from app.repositories.analisis import AnalisisRepository

        tid = seed_tenant_admin["tenant_id"]
        repo = AnalisisRepository(db_session, tid)
        materia_id = seed_estructura["materia_id"]

        resultado = await repo.reportes_rapidos(materia_id)

        assert "total_alumnos" in resultado
        assert "total_calificaciones" in resultado
        assert "promedio_general" in resultado
        assert "total_aprobados" in resultado
        assert "total_no_aprobados" in resultado
        assert "desglose_por_actividad" in resultado

    async def test_reportes_metrics_values(
        self, analisis_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
        seed_calificaciones: dict[str, Any],
    ) -> None:
        """TRIANGULATE: valores de métricas correctos."""
        from app.repositories.analisis import AnalisisRepository

        tid = seed_tenant_admin["tenant_id"]
        repo = AnalisisRepository(db_session, tid)
        materia_id = seed_estructura["materia_id"]

        resultado = await repo.reportes_rapidos(materia_id)

        assert resultado["total_alumnos"] == 3
        assert resultado["total_calificaciones"] == 4
        assert resultado["promedio_general"] is not None
        assert resultado["total_aprobados"] + resultado["total_no_aprobados"] == resultado["total_calificaciones"]

    async def test_reportes_vacio(
        self, analisis_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
    ) -> None:
        """TRIANGULATE: materia sin calificaciones → ceros."""
        from app.repositories.analisis import AnalisisRepository

        tid = seed_tenant_admin["tenant_id"]
        repo = AnalisisRepository(db_session, tid)
        materia_id = seed_estructura["materia_id"]

        resultado = await repo.reportes_rapidos(materia_id)

        assert resultado["total_calificaciones"] == 0
        assert resultado["promedio_general"] == 0


# ═══════════════════════════════════════════════════════════════
# 2.4 — notas_finales
# ═══════════════════════════════════════════════════════════════

class TestNotasFinales:
    """RED: AnalisisRepository.notas_finales no existe aún."""

    async def test_notas_finales_promedio(
        self, analisis_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
        seed_calificaciones: dict[str, Any],
    ) -> None:
        """RED 2.4: promedio de actividades seleccionadas."""
        from app.repositories.analisis import AnalisisRepository

        tid = seed_tenant_admin["tenant_id"]
        repo = AnalisisRepository(db_session, tid)
        materia_id = seed_estructura["materia_id"]

        resultado = await repo.notas_finales(materia_id, ["TP1"])

        # Juan: TP1=75
        juan = next((r for r in resultado if "Perez" in r.get("alumno_nombre", "")), None)
        assert juan is not None
        assert juan["promedio"] == 75.0

        # Maria: TP1=45
        maria = next((r for r in resultado if "Gomez" in r.get("alumno_nombre", "")), None)
        assert maria is not None
        assert maria["promedio"] == 45.0

    async def test_notas_finales_excluye_textuales(
        self, analisis_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
        seed_calificaciones: dict[str, Any],
    ) -> None:
        """TRIANGULATE: notas textuales excluidas del promedio (solo numéricas)."""
        from app.repositories.analisis import AnalisisRepository

        tid = seed_tenant_admin["tenant_id"]
        repo = AnalisisRepository(db_session, tid)
        materia_id = seed_estructura["materia_id"]

        # TP2 for Juan is textual (Satisfactorio) — should not affect average
        resultado = await repo.notas_finales(materia_id, ["TP1", "TP2"])

        juan = next((r for r in resultado if "Perez" in r.get("alumno_nombre", "")), None)
        assert juan is not None
        # Only TP1 numeric=75 for Juan, TP2 is textual, so average = 75
        assert juan["promedio"] == 75.0

    async def test_notas_finales_sin_actividades(
        self, analisis_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
    ) -> None:
        """TRIANGULATE: lista vacía de actividades → resultado vacío."""
        from app.repositories.analisis import AnalisisRepository

        tid = seed_tenant_admin["tenant_id"]
        repo = AnalisisRepository(db_session, tid)
        materia_id = seed_estructura["materia_id"]

        resultado = await repo.notas_finales(materia_id, [])
        assert resultado == []


# ═══════════════════════════════════════════════════════════════
# 2.5 — tps_sin_corregir
# ═══════════════════════════════════════════════════════════════

class TestTpsSinCorregir:
    """RED: AnalisisRepository.tps_sin_corregir no existe aún."""

    async def test_detecta_textual_sin_calificar(
        self, analisis_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
    ) -> None:
        """RED 2.5: actividad textual sin calificación aparece."""
        from app.models.calificaciones import Calificacion, OrigenCalificacion
        from app.repositories.analisis import AnalisisRepository

        tid = seed_tenant_admin["tenant_id"]
        repo = AnalisisRepository(db_session, tid)
        materia_id = seed_estructura["materia_id"]

        # Add a textual calificacion for Juan (TP2 already exists as textual)
        # But we need NO calificacion for a textual activity to detect it
        # Add a calificacion for TP1 (numeric) only — TP2 (textual) is the one without calif
        # Actually, in our seed we DO have calif for TP2 for Juan (textual Satisfactorio)
        # Let's add a new textual activity "Trabajo Final" without calificacion
        # We need to generate the data properly: what activities are "expected"?

        # For this test, we need to define what activities should exist.
        # The method tps_sin_corregir finds EntradaPadron records for the materia
        # and cross-references against Calificacion for textual-scale activities.
        # Since there's no "expected activities" list (unlike listar_atrasados which
        # determines activities from calificaciones), we need to seed some expected
        # data. The design says "actividades textuales que aparecen en el padrón
        # pero no tienen calificación". Let me add a textual Calificacion record
        # that indicates submission but not grading.

        # Actually, re-reading the task: "Cross-reference against Calificacion,
        # Only report textual-scale activities (RN-07/08) — ignore numeric activities without grades"
        # This detects activities that ARE in the calificaciones table as submitted
        # but without a proper grade. But we don't have that data model.
        # 
        # The simpler interpretation: find all students in the active padron,
        # find all Calificacion records for those students, report textual
        # activities missing from those records.
        # Since Juan has TP1 (numeric, ok), TP2 (textual, has calif), TP3 missing
        # TP3 doesn't exist as an activity in calificaciones at all.
        # But for "sin corregir", we look at activities expected to be there.

        # Given the design: the task says to use Calificacion records as the
        # source of "what activities exist" for a materia.
        # Activities that are textual-scale AND don't have a record for a student
        # are considered "sin corregir".

        # The simplest test: add a textual calificacion for Carlos (who has none)
        Carlos_id = seed_padron_activo["alumno3_id"]
        # Check that Carlos with no califs has missing textual activities
        resultado = await repo.tps_sin_corregir(materia_id)
        
        # Since we have calificaciones for TP1 (numeric) and TP2 (textual),
        # but only for Juan and Maria, Carlos is missing both.
        # Per RN-08, we ignore numeric (TP1), only report textual (TP2).
        carlos_items = [r for r in resultado if r["alumno_nombre"] == "Carlos Lopez"]
        tp2_carlos = [r for r in carlos_items if r["actividad"] == "TP2"]
        assert len(tp2_carlos) >= 1, "Carlos sin TP2 textual debe aparecer como sin corregir"

        # Verify format
        for item in resultado:
            assert "alumno_nombre" in item
            assert "actividad" in item
            assert "materia_id" in item

    async def test_excluye_actividades_numericas(
        self, analisis_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
        seed_calificaciones: dict[str, Any],
    ) -> None:
        """TRIANGULATE: RN-08 excluye actividades numéricas."""
        from app.repositories.analisis import AnalisisRepository

        tid = seed_tenant_admin["tenant_id"]
        repo = AnalisisRepository(db_session, tid)
        materia_id = seed_estructura["materia_id"]

        resultado = await repo.tps_sin_corregir(materia_id)

        # TP1 is numeric — should NOT appear in results
        tp1_items = [r for r in resultado if r["actividad"] == "TP1"]
        assert len(tp1_items) == 0, "RN-08: actividades numéricas no deben aparecer"

    async def test_excluye_actividades_ya_calificadas(
        self, analisis_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
        seed_calificaciones: dict[str, Any],
    ) -> None:
        """TRIANGULATE: textual ya calificada no aparece."""
        from app.repositories.analisis import AnalisisRepository

        tid = seed_tenant_admin["tenant_id"]
        repo = AnalisisRepository(db_session, tid)
        materia_id = seed_estructura["materia_id"]

        resultado = await repo.tps_sin_corregir(materia_id)

        # Juan has TP2 textual with calificacion — should NOT appear
        juan_tp2 = [r for r in resultado if "Perez" in r.get("alumno_nombre", "") and r["actividad"] == "TP2"]
        assert len(juan_tp2) == 0, "TP2 de Juan ya está calificado, no debe aparecer"


# ═══════════════════════════════════════════════════════════════
# 2.6 — monitor
# ═══════════════════════════════════════════════════════════════

class TestMonitorGeneral:
    """RED: AnalisisRepository.monitor no existe aún."""

    async def test_monitor_requiere_filtro(
        self, analisis_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        """RED 2.6: sin filtros válidos lanza error."""
        from app.repositories.analisis import AnalisisRepository

        tid = seed_tenant_admin["tenant_id"]
        repo = AnalisisRepository(db_session, tid)

        with pytest.raises(ValueError):
            await repo.monitor({})

    async def test_monitor_con_materia(
        self, analisis_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
        seed_calificaciones: dict[str, Any],
    ) -> None:
        """RED 2.6: filtro por materia retorna datos."""
        from app.repositories.analisis import AnalisisRepository

        tid = seed_tenant_admin["tenant_id"]
        repo = AnalisisRepository(db_session, tid)
        materia_id = seed_estructura["materia_id"]

        resultado = await repo.monitor({"materia_id": materia_id})

        assert "data" in resultado
        assert "total" in resultado
        assert resultado["total"] > 0

    async def test_monitor_paginacion(
        self, analisis_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
        seed_calificaciones: dict[str, Any],
    ) -> None:
        """TRIANGULATE: paginación limita resultados."""
        from app.repositories.analisis import AnalisisRepository

        tid = seed_tenant_admin["tenant_id"]
        repo = AnalisisRepository(db_session, tid)
        materia_id = seed_estructura["materia_id"]

        resultado = await repo.monitor({"materia_id": materia_id}, limit=1)
        assert len(resultado["data"]) <= 1
        assert resultado["total"] >= 2  # At least 3 students


# ═══════════════════════════════════════════════════════════════
# 2.7 — monitor_por_asignaciones
# ═══════════════════════════════════════════════════════════════

class TestMonitorPorAsignaciones:
    """RED: AnalisisRepository.monitor_por_asignaciones no existe aún."""

    async def test_monitor_por_asignaciones_filtra(
        self, analisis_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
    ) -> None:
        """RED 2.7: filtrar por asignaciones limita scope."""
        from app.repositories.analisis import AnalisisRepository
        from app.models.usuarios_asignaciones import Asignacion, Usuario

        tid = seed_tenant_admin["tenant_id"]
        repo = AnalisisRepository(db_session, tid)
        materia_id = seed_estructura["materia_id"]

        # Create asignacion for materia
        usuario = Usuario(
            tenant_id=tid, nombre="Tutor",
            apellidos="Uno", email="tutor@test.com",
        )
        db_session.add(usuario)
        await db_session.flush()
        asignacion = Asignacion(
            tenant_id=tid, usuario_id=usuario.id, rol="TUTOR",
            materia_id=materia_id, desde=date(2026, 1, 1),
        )
        db_session.add(asignacion)
        await db_session.flush()
        await db_session.commit()

        resultado = await repo.monitor_por_asignaciones(
            {"materia_id": materia_id},
            [asignacion.id],
        )

        assert "data" in resultado
        assert resultado["total"] >= 0


# ═══════════════════════════════════════════════════════════════
# 2.8 — monitor_con_fechas
# ═══════════════════════════════════════════════════════════════

class TestMonitorConFechas:
    """RED: AnalisisRepository.monitor_con_fechas no existe aún."""

    async def test_monitor_con_fechas_filtra_por_rango(
        self, analisis_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
        seed_calificaciones: dict[str, Any],
    ) -> None:
        """RED 2.8: rango de fechas filtra calificaciones."""
        from app.repositories.analisis import AnalisisRepository

        tid = seed_tenant_admin["tenant_id"]
        repo = AnalisisRepository(db_session, tid)
        materia_id = seed_estructura["materia_id"]

        desde = datetime(2020, 1, 1, tzinfo=UTC)
        hasta = datetime(2020, 12, 31, tzinfo=UTC)
        resultado = await repo.monitor_con_fechas(
            {"materia_id": materia_id},
            desde=desde, hasta=hasta,
        )

        assert "data" in resultado
        # No calificaciones in 2020 → empty but valid
        assert resultado["total"] == 0
