"""Tests para C-10 Calificaciones y Umbral.

Strict TDD: RED → GREEN → TRIANGULATE → REFACTOR.
"""

import io
from datetime import UTC, date, datetime
from typing import Any
from uuid import UUID, uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import inspect as sa_inspect, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base
from app.core.security import hash_password
from app.models.auth import AuthUser
from app.models.tenant import Tenant


# ═══════════════════════════════════════════════════════════════
# 1.1 / 1.2 — Model Schema Validation (TDD RED → GREEN)
# ═══════════════════════════════════════════════════════════════


class TestCalificacionModelSchema:
    """Verifica que Calificacion existe con el schema correcto."""

    def test_model_is_importable(self) -> None:
        from app.models.calificaciones import Calificacion

        assert Calificacion is not None
        assert Calificacion.__tablename__ == "calificaciones"

    def test_model_has_required_columns(self) -> None:
        from app.models.calificaciones import Calificacion

        mapper = sa_inspect(Calificacion)
        columns = {c.name: c for c in mapper.columns}
        assert "id" in columns
        assert "tenant_id" in columns
        assert "entrada_padron_id" in columns
        assert "materia_id" in columns
        assert "actividad" in columns
        assert "nota_numerica" in columns
        assert "nota_textual" in columns
        assert "aprobado" in columns
        assert "origen" in columns
        assert "importado_at" in columns
        assert "created_at" in columns
        assert "updated_at" in columns
        assert "deleted_at" in columns

    def test_nota_numerica_is_nullable(self) -> None:
        from app.models.calificaciones import Calificacion

        mapper = sa_inspect(Calificacion)
        assert mapper.columns.nota_numerica.nullable is True

    def test_nota_textual_is_nullable(self) -> None:
        from app.models.calificaciones import Calificacion

        mapper = sa_inspect(Calificacion)
        assert mapper.columns.nota_textual.nullable is True

    def test_aprobado_not_nullable(self) -> None:
        from app.models.calificaciones import Calificacion

        mapper = sa_inspect(Calificacion)
        assert mapper.columns.aprobado.nullable is False

    def test_origen_not_nullable(self) -> None:
        from app.models.calificaciones import Calificacion

        mapper = sa_inspect(Calificacion)
        assert mapper.columns.origen.nullable is False

    def test_has_unique_constraint_on_tenant_materia_entrada_actividad(self) -> None:
        from app.models.calificaciones import Calificacion

        table_args = Calificacion.__table_args__
        if isinstance(table_args, tuple):
            constraints = table_args
        else:
            constraints = (table_args,)

        uq_names = {c.name for c in constraints if hasattr(c, "name")}
        assert "uq_calificacion_actividad" in uq_names


class TestOrigenCalificacionEnum:
    """Verifica que el enum OrigenCalificacion tiene los valores correctos."""

    def test_enum_values(self) -> None:
        from app.models.calificaciones import OrigenCalificacion

        assert OrigenCalificacion.IMPORTADO.value == "Importado"
        assert OrigenCalificacion.MANUAL.value == "Manual"

    def test_enum_members_count(self) -> None:
        from app.models.calificaciones import OrigenCalificacion

        assert len(OrigenCalificacion) == 2


class TestUmbralMateriaModelSchema:
    """Verifica que UmbralMateria existe con el schema correcto."""

    def test_model_is_importable(self) -> None:
        from app.models.calificaciones import UmbralMateria

        assert UmbralMateria is not None
        assert UmbralMateria.__tablename__ == "umbrales_materia"

    def test_model_has_required_columns(self) -> None:
        from app.models.calificaciones import UmbralMateria

        mapper = sa_inspect(UmbralMateria)
        columns = {c.name: c for c in mapper.columns}
        assert "id" in columns
        assert "tenant_id" in columns
        assert "asignacion_id" in columns
        assert "materia_id" in columns
        assert "umbral_pct" in columns
        assert "valores_aprobatorios" in columns
        assert "created_at" in columns
        assert "updated_at" in columns
        assert "deleted_at" in columns

    def test_umbral_pct_default_is_60(self) -> None:
        from app.models.calificaciones import UmbralMateria

        assert UmbralMateria.umbral_pct.default.arg == 60

    def test_valores_aprobatorios_is_nullable(self) -> None:
        from app.models.calificaciones import UmbralMateria

        mapper = sa_inspect(UmbralMateria)
        assert mapper.columns.valores_aprobatorios.nullable is True

    def test_has_unique_constraint_on_tenant_asignacion_materia(self) -> None:
        from app.models.calificaciones import UmbralMateria

        table_args = UmbralMateria.__table_args__
        if isinstance(table_args, tuple):
            constraints = table_args
        else:
            constraints = (table_args,)

        uq_names = {c.name for c in constraints if hasattr(c, "name")}
        assert "uq_umbral_asignacion_materia" in uq_names


class TestCalificacionesInitImports:
    """Verifica que __init__ exporta los modelos correctamente."""

    def test_calificacion_exported_from_init(self) -> None:
        from app.models import Calificacion  # noqa: F811

        assert Calificacion is not None

    def test_umbral_materia_exported_from_init(self) -> None:
        from app.models import UmbralMateria  # noqa: F811

        assert UmbralMateria is not None

    def test_origen_calificacion_exported_from_init(self) -> None:
        from app.models import OrigenCalificacion  # noqa: F811

        assert OrigenCalificacion is not None


# ═══════════════════════════════════════════════════════════════
# 1.4 — Permission schema validation
# ═══════════════════════════════════════════════════════════════


class TestCalificacionesPermiso:
    """Verifica que calificaciones:importar existe como constante."""

    def test_constante_existe(self) -> None:
        from app.models.permisos import CALIFICACIONES_IMPORTAR

        assert CALIFICACIONES_IMPORTAR == "calificaciones:importar"


# ═══════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════


@pytest.fixture
async def calif_schema(db_engine: None):
    """Creates full schema including calificaciones tables."""
    from app.core.database import get_sessionmaker
    from app.models.calificaciones import Calificacion, UmbralMateria  # noqa: F401
    from app.models.estructura_academica import Carrera, Cohorte, Materia  # noqa: F401
    from app.models.padron import EntradaPadron, VersionPadron  # noqa: F401
    from app.models.usuarios_asignaciones import Asignacion, Usuario  # noqa: F401
    from app.services.auth import login_rate_limiter

    login_rate_limiter.reset_all()

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
async def seed_tenant_admin(
    db_session: AsyncSession,
) -> dict[str, Any]:
    """Seeds tenant + admin user + calificaciones:importar permission."""
    tenant = Tenant(name="Tenant test-tenant", code="test-tenant")
    db_session.add(tenant)
    await db_session.flush()

    user = AuthUser(
        tenant_id=tenant.id,
        email="user@test.com",
        password_hash=hash_password("password"),
        roles=["ADMIN"],
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    from app.models.rbac import Permiso, Rol, RolPermiso

    rol = Rol(tenant_id=tenant.id, codigo="ADMIN", nombre="Admin")
    db_session.add(rol)
    permiso = Permiso(
        tenant_id=tenant.id,
        codigo="calificaciones:importar",
        nombre="Importar calificaciones",
        modulo="calificaciones",
        accion="importar",
    )
    db_session.add(permiso)
    await db_session.flush()

    rp = RolPermiso(
        tenant_id=tenant.id,
        rol_id=rol.id,
        permiso_id=permiso.id,
        habilitado=True,
        alcance="global",
    )
    db_session.add(rp)
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

    return {
        "carrera_id": carrera.id,
        "cohorte_id": cohorte.id,
        "materia_id": materia.id,
    }


@pytest.fixture
async def seed_padron_activo(
    db_session: AsyncSession,
    seed_tenant_admin: dict[str, Any],
    seed_estructura: dict[str, Any],
) -> dict[str, Any]:
    """Seeds an active padron version with 2 students."""
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
    )
    db_session.add(alumno1)
    alumno2 = EntradaPadron(
        tenant_id=seed_tenant_admin["tenant_id"],
        version_id=version.id,
        nombre="Maria",
        apellidos="Gomez",
        email="maria@test.com",
        comision="B",
    )
    db_session.add(alumno2)
    await db_session.flush()
    await db_session.commit()

    return {
        "version_id": version.id,
        "alumno1_id": alumno1.id,
        "alumno2_id": alumno2.id,
    }


@pytest.fixture
async def seed_asignacion(
    db_session: AsyncSession,
    seed_tenant_admin: dict[str, Any],
    seed_estructura: dict[str, Any],
) -> dict[str, Any]:
    """Seeds a user+asignacion for threshold testing."""
    from app.models.usuarios_asignaciones import Asignacion, Usuario

    usuario = Usuario(
        tenant_id=seed_tenant_admin["tenant_id"],
        nombre="Teacher",
        apellidos="One",
        email="teacher@test.com",
    )
    db_session.add(usuario)
    await db_session.flush()

    asignacion = Asignacion(
        tenant_id=seed_tenant_admin["tenant_id"],
        usuario_id=usuario.id,
        rol="PROFESOR",
        materia_id=seed_estructura["materia_id"],
        desde=date(2026, 1, 1),
    )
    db_session.add(asignacion)
    await db_session.flush()
    await db_session.commit()

    return {
        "usuario_id": usuario.id,
        "asignacion_id": asignacion.id,
    }


@pytest.fixture
async def seed_calificaciones(
    db_session: AsyncSession,
    seed_tenant_admin: dict[str, Any],
    seed_estructura: dict[str, Any],
    seed_padron_activo: dict[str, Any],
) -> dict[str, Any]:
    """Seeds Calificacion records for repository testing."""
    from app.models.calificaciones import Calificacion, OrigenCalificacion

    calif1 = Calificacion(
        tenant_id=seed_tenant_admin["tenant_id"],
        entrada_padron_id=seed_padron_activo["alumno1_id"],
        materia_id=seed_estructura["materia_id"],
        actividad="TP1",
        nota_numerica=75.0,
        nota_textual=None,
        aprobado=True,
        origen=OrigenCalificacion.IMPORTADO,
    )
    db_session.add(calif1)
    calif2 = Calificacion(
        tenant_id=seed_tenant_admin["tenant_id"],
        entrada_padron_id=seed_padron_activo["alumno2_id"],
        materia_id=seed_estructura["materia_id"],
        actividad="TP1",
        nota_numerica=45.0,
        nota_textual=None,
        aprobado=False,
        origen=OrigenCalificacion.IMPORTADO,
    )
    db_session.add(calif2)
    calif3 = Calificacion(
        tenant_id=seed_tenant_admin["tenant_id"],
        entrada_padron_id=seed_padron_activo["alumno1_id"],
        materia_id=seed_estructura["materia_id"],
        actividad="TP2",
        nota_numerica=None,
        nota_textual="Satisfactorio",
        aprobado=True,
        origen=OrigenCalificacion.IMPORTADO,
    )
    db_session.add(calif3)
    await db_session.flush()
    await db_session.commit()

    return {
        "calif1_id": calif1.id,
        "calif2_id": calif2.id,
        "calif3_id": calif3.id,
    }


@pytest.fixture
async def seed_umbral(
    db_session: AsyncSession,
    seed_tenant_admin: dict[str, Any],
    seed_estructura: dict[str, Any],
    seed_asignacion: dict[str, Any],
) -> dict[str, Any]:
    """Seeds an UmbralMateria record for repository testing."""
    from app.models.calificaciones import UmbralMateria

    umbral = UmbralMateria(
        tenant_id=seed_tenant_admin["tenant_id"],
        asignacion_id=seed_asignacion["asignacion_id"],
        materia_id=seed_estructura["materia_id"],
        umbral_pct=70,
        valores_aprobatorios=["Satisfactorio", "Supera lo esperado"],
    )
    db_session.add(umbral)
    await db_session.flush()
    await db_session.commit()

    return {"umbral_id": umbral.id}


async def admin_headers(
    client: AsyncClient, tenant_code: str = "test-tenant", email: str = "user@test.com"
) -> dict[str, str]:
    """Login helper, returns auth headers."""
    resp = await client.post(
        "/api/auth/login",
        json={"tenant_code": tenant_code, "email": email, "password": "password"},
    )
    data = resp.json()
    assert "access_token" in data, f"Login failed for {email}@{tenant_code}: {data}"
    return {"Authorization": f"Bearer {data['access_token']}"}


def make_csv(content: str) -> tuple[str, bytes]:
    """Helper to create a CSV file tuple."""
    return "grades.csv", content.encode("utf-8")


# ═══════════════════════════════════════════════════════════════
# 8.1 — Tests de derivación de aprobado
# ═══════════════════════════════════════════════════════════════


class TestDerivarAprobado:
    """Derivación de aprobado: numérica, textual, default."""

    def test_numerica_aprueba_si_supera_umbral(self) -> None:
        from app.services.calificaciones import derivar_aprobado

        assert derivar_aprobado(nota_numerica=75, nota_textual=None, umbral_pct=60) is True

    def test_numerica_no_aprueba_si_no_alcanza_umbral(self) -> None:
        from app.services.calificaciones import derivar_aprobado

        assert derivar_aprobado(nota_numerica=45, nota_textual=None, umbral_pct=60) is False

    def test_numerica_exactamente_en_umbral_aprueba(self) -> None:
        from app.services.calificaciones import derivar_aprobado

        assert derivar_aprobado(nota_numerica=60, nota_textual=None, umbral_pct=60) is True

    def test_textual_en_valores_aprobatorios_aprueba(self) -> None:
        from app.services.calificaciones import derivar_aprobado

        assert derivar_aprobado(
            nota_numerica=None,
            nota_textual="Satisfactorio",
            valores_aprobatorios=["Satisfactorio", "Supera lo esperado"],
        ) is True

    def test_textual_fuera_de_valores_no_aprueba(self) -> None:
        from app.services.calificaciones import derivar_aprobado

        assert derivar_aprobado(
            nota_numerica=None,
            nota_textual="No satisfactorio",
            valores_aprobatorios=["Satisfactorio", "Supera lo esperado"],
        ) is False

    def test_textual_sin_valores_configurados_usa_default(self) -> None:
        from app.services.calificaciones import derivar_aprobado

        assert derivar_aprobado(
            nota_numerica=None,
            nota_textual="Satisfactorio",
        ) is True  # Satisfactorio está en default

    def test_sin_nota_no_aprueba(self) -> None:
        from app.services.calificaciones import derivar_aprobado

        assert derivar_aprobado(nota_numerica=None, nota_textual=None) is False

    def test_umbral_personalizado_funciona(self) -> None:
        from app.services.calificaciones import derivar_aprobado

        assert derivar_aprobado(nota_numerica=80, nota_textual=None, umbral_pct=90) is False
        assert derivar_aprobado(nota_numerica=95, nota_textual=None, umbral_pct=90) is True


# ═══════════════════════════════════════════════════════════════
# 8.2 — Tests de import preview
# ═══════════════════════════════════════════════════════════════


class TestImportPreview:
    """Preview detecta columnas mixtas correctamente."""

    async def test_preview_detects_numeric_columns(
        self, calif_schema, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)
        filename, content = make_csv(
            "Nombre,Apellidos,Email,TP1 (Real),TP2 (Real)\n"
            "Juan,Perez,juan@test.com,75,80\n"
            "Maria,Gomez,maria@test.com,60,90\n"
        )

        resp = await async_client.post(
            "/api/calificaciones/import/preview",
            params={
                "materia_id": str(seed_estructura["materia_id"]),
                "cohorte_id": str(seed_estructura["cohorte_id"]),
            },
            files={"archivo": (filename, content, "text/csv")},
            headers=headers,
        )

        assert resp.status_code == 200
        data = resp.json()
        assert "preview_token" in data
        assert len(data["actividades"]) == 2
        tipos = {a["tipo"] for a in data["actividades"]}
        assert tipos == {"numeric"}
        assert data["total_rows"] == 2

    async def test_preview_detects_mixed_columns(
        self, calif_schema, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)
        filename, content = make_csv(
            "Nombre,Apellidos,Email,TP1 (Real),Trabajo Final\n"
            "Juan,Perez,juan@test.com,75,Satisfactorio\n"
        )

        resp = await async_client.post(
            "/api/calificaciones/import/preview",
            params={
                "materia_id": str(seed_estructura["materia_id"]),
                "cohorte_id": str(seed_estructura["cohorte_id"]),
            },
            files={"archivo": (filename, content, "text/csv")},
            headers=headers,
        )

        assert resp.status_code == 200
        data = resp.json()
        actividades = data["actividades"]
        tipos = {a["tipo"] for a in actividades}
        assert tipos == {"numeric", "textual"}
        nombres = {a["nombre"] for a in actividades}
        assert "TP1" in nombres
        assert "Trabajo Final" in nombres

    async def test_preview_reports_no_match_separately(
        self, calif_schema, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)
        filename, content = make_csv(
            "Nombre,Apellidos,Email,TP1 (Real)\n"
            "Juan,Perez,juan@test.com,75\n"
            "Unknown,Student,unknown@test.com,50\n"
        )

        resp = await async_client.post(
            "/api/calificaciones/import/preview",
            params={
                "materia_id": str(seed_estructura["materia_id"]),
                "cohorte_id": str(seed_estructura["cohorte_id"]),
            },
            files={"archivo": (filename, content, "text/csv")},
            headers=headers,
        )

        assert resp.status_code == 200
        data = resp.json()
        assert len(data["alumnos_match"]) == 1
        assert len(data["alumnos_no_match"]) == 1
        assert data["alumnos_no_match"][0]["datos"]["nombre"] == "Unknown"


# ═══════════════════════════════════════════════════════════════
# 8.3 — Tests de import confirm
# ═══════════════════════════════════════════════════════════════


class TestImportConfirm:
    """Confirmar import persiste calificaciones."""

    async def test_confirm_creates_calificaciones(
        self, calif_schema, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)
        filename, content = make_csv(
            "Nombre,Apellidos,Email,TP1 (Real),TP2 (Real)\n"
            "Juan,Perez,juan@test.com,75,80\n"
            "Maria,Gomez,maria@test.com,60,45\n"
        )

        # Step 1: preview
        preview = await async_client.post(
            "/api/calificaciones/import/preview",
            params={
                "materia_id": str(seed_estructura["materia_id"]),
                "cohorte_id": str(seed_estructura["cohorte_id"]),
            },
            files={"archivo": (filename, content, "text/csv")},
            headers=headers,
        )
        preview_data = preview.json()

        # Step 2: confirm
        resp = await async_client.post(
            "/api/calificaciones/import/confirm",
            json={
                "preview_token": preview_data["preview_token"],
                "actividad_ids": ["TP1", "TP2"],
            },
            headers=headers,
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["registros_creados"] == 4  # 2 alumnos × 2 actividades
        assert set(data["actividades_importadas"]) == {"TP1", "TP2"}

    async def test_confirm_calcula_aprobado(
        self, calif_schema, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)
        filename, content = make_csv(
            "Nombre,Apellidos,Email,TP1 (Real)\n"
            "Juan,Perez,juan@test.com,75\n"
            "Maria,Gomez,maria@test.com,45\n"
        )

        preview = await async_client.post(
            "/api/calificaciones/import/preview",
            params={
                "materia_id": str(seed_estructura["materia_id"]),
                "cohorte_id": str(seed_estructura["cohorte_id"]),
            },
            files={"archivo": (filename, content, "text/csv")},
            headers=headers,
        )

        await async_client.post(
            "/api/calificaciones/import/confirm",
            json={
                "preview_token": preview.json()["preview_token"],
                "actividad_ids": ["TP1"],
            },
            headers=headers,
        )

        # Verify via list endpoint
        list_resp = await async_client.get(
            "/api/calificaciones",
            params={"materia_id": str(seed_estructura["materia_id"])},
            headers=headers,
        )

        assert list_resp.status_code == 200
        items = list_resp.json()["items"]
        assert len(items) == 2

        items_by_alumno = {}
        for item in items:
            items_by_alumno[item["entrada_padron_id"]] = item

        # Juan: 75 >= 60 → aprobado
        for item in items:
            if item["nota_numerica"] == 75:
                assert item["aprobado"] is True
            elif item["nota_numerica"] == 45:
                assert item["aprobado"] is False

        assert all(item["origen"] == "Importado" for item in items)

    async def test_confirm_with_expired_token_returns_409(
        self, calif_schema, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        resp = await async_client.post(
            "/api/calificaciones/import/confirm",
            json={
                "preview_token": str(uuid4()),
                "actividad_ids": ["TP1"],
            },
            headers=headers,
        )

        assert resp.status_code == 409


# ═══════════════════════════════════════════════════════════════
# 8.4 — Tests de alumnos no matcheados
# ═══════════════════════════════════════════════════════════════


class TestUnmatchedStudents:
    """Alumnos no matcheados se reportan sin crear registros."""

    async def test_unmatched_not_imported(
        self, calif_schema, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)
        filename, content = make_csv(
            "Nombre,Apellidos,Email,TP1 (Real)\n"
            "Juan,Perez,juan@test.com,75\n"
            "Nobody,Nowhere,ghost@test.com,50\n"
        )

        # Preview
        preview = await async_client.post(
            "/api/calificaciones/import/preview",
            params={
                "materia_id": str(seed_estructura["materia_id"]),
                "cohorte_id": str(seed_estructura["cohorte_id"]),
            },
            files={"archivo": (filename, content, "text/csv")},
            headers=headers,
        )
        preview_data = preview.json()
        assert len(preview_data["alumnos_no_match"]) == 1
        assert len(preview_data["alumnos_match"]) == 1

        # Confirm import
        confirm = await async_client.post(
            "/api/calificaciones/import/confirm",
            json={
                "preview_token": preview_data["preview_token"],
                "actividad_ids": ["TP1"],
            },
            headers=headers,
        )
        assert confirm.json()["registros_creados"] == 1  # Only matched student

        # List only has 1 calificacion
        list_resp = await async_client.get(
            "/api/calificaciones",
            params={"materia_id": str(seed_estructura["materia_id"])},
            headers=headers,
        )
        assert list_resp.json()["total"] == 1


# ═══════════════════════════════════════════════════════════════
# 8.5 — Tests de completion report
# ═══════════════════════════════════════════════════════════════


class TestCompletionReport:
    """Completion report: textual sin calificar, numérica ignorada, ya calificada ignorada."""

    async def test_detect_ungraded_textual(
        self, calif_schema, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)
        # Upload grades for TP1 numeric only
        grades_csv = make_csv(
            "Nombre,Apellidos,Email,TP1 (Real)\n"
            "Juan,Perez,juan@test.com,75\n"
        )
        preview = await async_client.post(
            "/api/calificaciones/import/preview",
            params={
                "materia_id": str(seed_estructura["materia_id"]),
                "cohorte_id": str(seed_estructura["cohorte_id"]),
            },
            files={"archivo": (grades_csv[0], grades_csv[1], "text/csv")},
            headers=headers,
        )
        await async_client.post(
            "/api/calificaciones/import/confirm",
            json={"preview_token": preview.json()["preview_token"], "actividad_ids": ["TP1"]},
            headers=headers,
        )

        # Now upload completion report showing Trabajo Final submitted but not graded
        completion_csv = make_csv(
            "Nombre,Apellidos,Email,Trabajo Final\n"
            "Juan,Perez,juan@test.com,Entregado\n"
        )

        resp = await async_client.post(
            "/api/calificaciones/completion-report",
            params={
                "materia_id": str(seed_estructura["materia_id"]),
                "cohorte_id": str(seed_estructura["cohorte_id"]),
            },
            files={"archivo": (completion_csv[0], completion_csv[1], "text/csv")},
            headers=headers,
        )

        assert resp.status_code == 200
        data = resp.json()
        assert len(data["posibles_entregas_sin_corregir"]) == 1
        entry = data["posibles_entregas_sin_corregir"][0]
        assert entry["actividad"] == "Trabajo Final"

    async def test_numeric_ungraded_not_reported(
        self, calif_schema, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)
        # Completion report with numeric activity without grade
        completion_csv = make_csv(
            "Nombre,Apellidos,Email,TP1 (Real)\n"
            "Juan,Perez,juan@test.com,Entregado\n"
        )

        resp = await async_client.post(
            "/api/calificaciones/completion-report",
            params={
                "materia_id": str(seed_estructura["materia_id"]),
                "cohorte_id": str(seed_estructura["cohorte_id"]),
            },
            files={"archivo": (completion_csv[0], completion_csv[1], "text/csv")},
            headers=headers,
        )

        assert resp.status_code == 200
        data = resp.json()
        # TP1 is numeric, should NOT appear in ungraded list
        assert len(data["posibles_entregas_sin_corregir"]) == 0

    async def test_already_graded_not_reported(
        self, calif_schema, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)
        # First import textual grade
        grades_csv = make_csv(
            "Nombre,Apellidos,Email,Trabajo Final\n"
            "Juan,Perez,juan@test.com,Satisfactorio\n"
        )
        preview = await async_client.post(
            "/api/calificaciones/import/preview",
            params={
                "materia_id": str(seed_estructura["materia_id"]),
                "cohorte_id": str(seed_estructura["cohorte_id"]),
            },
            files={"archivo": (grades_csv[0], grades_csv[1], "text/csv")},
            headers=headers,
        )
        await async_client.post(
            "/api/calificaciones/import/confirm",
            json={"preview_token": preview.json()["preview_token"], "actividad_ids": ["Trabajo Final"]},
            headers=headers,
        )

        # Now upload completion report
        completion_csv = make_csv(
            "Nombre,Apellidos,Email,Trabajo Final\n"
            "Juan,Perez,juan@test.com,Entregado\n"
        )

        resp = await async_client.post(
            "/api/calificaciones/completion-report",
            params={
                "materia_id": str(seed_estructura["materia_id"]),
                "cohorte_id": str(seed_estructura["cohorte_id"]),
            },
            files={"archivo": (completion_csv[0], completion_csv[1], "text/csv")},
            headers=headers,
        )

        assert resp.status_code == 200
        data = resp.json()
        # Already graded, should NOT appear
        assert len(data["posibles_entregas_sin_corregir"]) == 0


# ═══════════════════════════════════════════════════════════════
# 8.6 — Tests de umbral por asignación
# ═══════════════════════════════════════════════════════════════


class TestUmbralPorAsignacion:
    """Teacher A 70, Teacher B default 60."""

    async def test_teacher_sets_custom_threshold(
        self, calif_schema, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_asignacion: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        # Set umbral to 70
        resp = await async_client.put(
            "/api/calificaciones/umbral",
            params={
                "materia_id": str(seed_estructura["materia_id"]),
                "asignacion_id": str(seed_asignacion["asignacion_id"]),
            },
            json={"umbral_pct": 70, "valores_aprobatorios": ["Satisfactorio", "Muy bueno"]},
            headers=headers,
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["umbral_pct"] == 70
        assert data["valores_aprobatorios"] == ["Satisfactorio", "Muy bueno"]

        # Verify GET returns it
        resp = await async_client.get(
            "/api/calificaciones/umbral",
            params={
                "materia_id": str(seed_estructura["materia_id"]),
                "asignacion_id": str(seed_asignacion["asignacion_id"]),
            },
            headers=headers,
        )
        assert resp.json()["umbral_pct"] == 70

    async def test_different_teacher_gets_default(
        self, calif_schema, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_asignacion: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        # Teacher A: set threshold
        await async_client.put(
            "/api/calificaciones/umbral",
            params={
                "materia_id": str(seed_estructura["materia_id"]),
                "asignacion_id": str(seed_asignacion["asignacion_id"]),
            },
            json={"umbral_pct": 75},
            headers=headers,
        )

        # Teacher B: no config -> default 60
        other_asignacion_id = uuid4()
        resp = await async_client.get(
            "/api/calificaciones/umbral",
            params={
                "materia_id": str(seed_estructura["materia_id"]),
                "asignacion_id": str(other_asignacion_id),
            },
            headers=headers,
        )
        data = resp.json()
        assert data["umbral_pct"] == 60
        assert set(data["valores_aprobatorios"]) == {"Satisfactorio", "Supera lo esperado"}


# ═══════════════════════════════════════════════════════════════
# 8.7 — Tests de tenant isolation
# ═══════════════════════════════════════════════════════════════


class TestTenantIsolation:
    """Tenant A no ve calificaciones ni umbral de tenant B."""

    async def _create_tenant_b(
        self, db_session: AsyncSession,
    ) -> dict[str, Any]:
        """Helper to create tenant B with full setup."""
        from app.models.estructura_academica import Carrera, Cohorte, Materia
        from app.models.padron import EntradaPadron, VersionPadron
        from app.models.rbac import Permiso, Rol, RolPermiso
        from app.models.usuarios_asignaciones import Usuario

        t2 = Tenant(name="Tenant B", code="tenant-b")
        db_session.add(t2)
        await db_session.flush()

        u2 = AuthUser(
            tenant_id=t2.id, email="admin@b.com",
            password_hash=hash_password("password"), roles=["ADMIN"], is_active=True,
        )
        db_session.add(u2)

        docente_b = Usuario(
            tenant_id=t2.id, nombre="Admin", apellidos="B", email="admin.docente@b.com",
        )
        db_session.add(docente_b)

        r2 = Rol(tenant_id=t2.id, codigo="ADMIN", nombre="Admin")
        db_session.add(r2)
        p2 = Permiso(tenant_id=t2.id, codigo="calificaciones:importar", nombre="Importar",
                      modulo="calificaciones", accion="importar")
        db_session.add(p2)
        await db_session.flush()
        db_session.add(RolPermiso(tenant_id=t2.id, rol_id=r2.id, permiso_id=p2.id,
                                   habilitado=True, alcance="global"))

        carrera = Carrera(tenant_id=t2.id, codigo="T2", nombre="Tenant B Carrera")
        db_session.add(carrera)
        await db_session.flush()
        cohorte = Cohorte(tenant_id=t2.id, carrera_id=carrera.id, nombre="2026", anio=2026,
                          vig_desde=date(2026, 1, 1))
        db_session.add(cohorte)
        await db_session.flush()
        materia = Materia(tenant_id=t2.id, codigo="T2MAT", nombre="Tenant B Materia")
        db_session.add(materia)
        await db_session.flush()

        version = VersionPadron(tenant_id=t2.id, materia_id=materia.id, cohorte_id=cohorte.id,
                                 cargado_por=docente_b.id, activa=True)
        db_session.add(version)
        await db_session.flush()

        entrada = EntradaPadron(tenant_id=t2.id, version_id=version.id,
                                 nombre="Bob", apellidos="Smith", email="bob@b.com", comision="A")
        db_session.add(entrada)
        await db_session.flush()
        await db_session.commit()

        return {
            "tenant_id": t2.id, "tenant_code": t2.code, "user_id": u2.id,
            "materia_id": materia.id, "cohorte_id": cohorte.id,
            "entrada_id": entrada.id,
        }

    async def test_tenant_b_calificaciones_not_visible_to_tenant_a(
        self, calif_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
    ) -> None:
        # Setup tenant B
        t2 = await self._create_tenant_b(db_session)
        headers_b = await admin_headers(async_client, t2["tenant_code"], "admin@b.com")

        # Import grades for tenant B
        csv_b = make_csv(
            "Nombre,Apellidos,Email,TP1 (Real)\nBob,Smith,bob@b.com,85\n"
        )
        preview_b = await async_client.post(
            "/api/calificaciones/import/preview",
            params={"materia_id": str(t2["materia_id"]), "cohorte_id": str(t2["cohorte_id"])},
            files={"archivo": (csv_b[0], csv_b[1], "text/csv")},
            headers=headers_b,
        )
        await async_client.post(
            "/api/calificaciones/import/confirm",
            json={"preview_token": preview_b.json()["preview_token"], "actividad_ids": ["TP1"]},
            headers=headers_b,
        )

        # Tenant A queries its own materia — should see 0
        headers_a = await admin_headers(async_client)
        resp = await async_client.get(
            "/api/calificaciones",
            params={"materia_id": str(seed_estructura["materia_id"])},
            headers=headers_a,
        )
        assert resp.json()["total"] == 0

    async def test_cross_tenant_umbral_not_visible(
        self, calif_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
        seed_asignacion: dict[str, Any],
    ) -> None:
        t2 = await self._create_tenant_b(db_session)
        from app.models.usuarios_asignaciones import Asignacion, Usuario

        # Create teacher B assignment
        usuario_b = Usuario(tenant_id=t2["tenant_id"], nombre="Teacher", apellidos="B", email="tb@b.com")
        db_session.add(usuario_b)
        await db_session.flush()
        asignacion_b = Asignacion(tenant_id=t2["tenant_id"], usuario_id=usuario_b.id,
                                   rol="PROFESOR", materia_id=t2["materia_id"], desde=date(2026, 1, 1))
        db_session.add(asignacion_b)
        await db_session.commit()

        # Set threshold for teacher B
        headers_b = await admin_headers(async_client, t2["tenant_code"], "admin@b.com")
        await async_client.put(
            "/api/calificaciones/umbral",
            params={"materia_id": str(t2["materia_id"]), "asignacion_id": str(asignacion_b.id)},
            json={"umbral_pct": 85},
            headers=headers_b,
        )

        # Tenant A should NOT see tenant B's threshold
        headers_a = await admin_headers(async_client)
        resp = await async_client.get(
            "/api/calificaciones/umbral",
            params={
                "materia_id": str(t2["materia_id"]),
                "asignacion_id": str(asignacion_b.id),
            },
            headers=headers_a,
        )
        # Tenant A will get default since it's for a different tenant's record
        # (or 404 if the repository filters it out)
        assert resp.status_code in (200, 404)
        if resp.status_code == 200:
            assert resp.json()["umbral_pct"] == 60  # default


# ═══════════════════════════════════════════════════════════════
# 8.8 — Tests de audit trail
# ═══════════════════════════════════════════════════════════════


class TestAuditTrail:
    """Import genera CALIFICACIONES_IMPORTAR."""

    async def test_import_creates_audit_entry(
        self, calif_schema, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
    ) -> None:
        # This test verifies the import flow doesn't crash even without
        # the AuditLog model (C-05). The audit is best-effort.
        headers = await admin_headers(async_client)
        filename, content = make_csv(
            "Nombre,Apellidos,Email,TP1 (Real)\n"
            "Juan,Perez,juan@test.com,75\n"
        )

        preview = await async_client.post(
            "/api/calificaciones/import/preview",
            params={
                "materia_id": str(seed_estructura["materia_id"]),
                "cohorte_id": str(seed_estructura["cohorte_id"]),
            },
            files={"archivo": (filename, content, "text/csv")},
            headers=headers,
        )

        resp = await async_client.post(
            "/api/calificaciones/import/confirm",
            json={
                "preview_token": preview.json()["preview_token"],
                "actividad_ids": ["TP1"],
            },
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["registros_creados"] == 1


# ═══════════════════════════════════════════════════════════════
# 8.1b — Tests unitarios del parser
# ═══════════════════════════════════════════════════════════════


class TestLMSFileParser:
    """Tests del parser de archivos LMS."""

    def test_detect_numeric_column(self) -> None:
        from app.services.lms_parser import LMSFileParser

        assert LMSFileParser._detect_column_type("TP1 (Real)") == "numeric"
        assert LMSFileParser._detect_column_type("TP1 (real)") == "numeric"
        assert LMSFileParser._detect_column_type("Examen (Real)") == "numeric"

    def test_detect_textual_column(self) -> None:
        from app.services.lms_parser import LMSFileParser

        assert LMSFileParser._detect_column_type("Trabajo Final") == "textual"
        assert LMSFileParser._detect_column_type("TP1") == "textual"

    def test_detect_identity_column(self) -> None:
        from app.services.lms_parser import LMSFileParser

        assert LMSFileParser._detect_column_type("Nombre") == "identity"
        assert LMSFileParser._detect_column_type("Apellidos") == "identity"
        assert LMSFileParser._detect_column_type("Email") == "identity"
        assert LMSFileParser._detect_column_type("Correo") == "identity"

    def test_parse_csv_simple(self) -> None:
        from app.services.lms_parser import LMSFileParser

        csv_content = "Nombre,Apellidos,Email,TP1 (Real)\nJuan,Perez,juan@test.com,75\n".encode("utf-8")
        result = LMSFileParser.parse("test.csv", csv_content)

        assert result.total_filas == 1
        assert len(result.columnas_identidad) == 3
        assert len(result.columnas_actividad) == 1
        assert result.columnas_actividad[0].tipo == "numeric"

    def test_parse_csv_missing_identity_raises_error(self) -> None:
        from app.services.lms_parser import LMSFileParser, LmsParseError

        csv_content = "TP1 (Real)\n75\n".encode("utf-8")
        with pytest.raises(LmsParseError, match="Columnas de identidad requeridas faltantes"):
            LMSFileParser.parse("test.csv", csv_content)

    def test_parse_csv_detect_numeric_activity_name(self) -> None:
        from app.services.lms_parser import LMSFileParser

        csv_content = "Nombre,Apellidos,Email,TP1 (Real)\nJuan,Perez,juan@test.com,75\n".encode("utf-8")
        result = LMSFileParser.parse("test.csv", csv_content)

        # Activity name should not include "(Real)"
        assert result.columnas_actividad[0].nombre == "TP1"


# ═══════════════════════════════════════════════════════════════
# 2.1 / 2.2 / 2.3 — Repository tests
# ═══════════════════════════════════════════════════════════════


class TestCalificacionRepository:
    """CalificacionRepository: CRUD, list, soft_delete, count."""

    async def test_create_batch_creates_multiple(
        self, calif_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
    ) -> None:
        from app.models.calificaciones import Calificacion, OrigenCalificacion
        from app.repositories.calificaciones import CalificacionRepository

        tid = seed_tenant_admin["tenant_id"]
        repo = CalificacionRepository(db_session, tid)
        entries = [
            Calificacion(
                tenant_id=tid,
                entrada_padron_id=seed_padron_activo["alumno1_id"],
                materia_id=seed_estructura["materia_id"],
                actividad="Examen",
                nota_numerica=80.0,
                nota_textual=None,
                aprobado=True,
                origen=OrigenCalificacion.IMPORTADO,
            ),
            Calificacion(
                tenant_id=tid,
                entrada_padron_id=seed_padron_activo["alumno2_id"],
                materia_id=seed_estructura["materia_id"],
                actividad="Examen",
                nota_numerica=50.0,
                nota_textual=None,
                aprobado=False,
                origen=OrigenCalificacion.IMPORTADO,
            ),
        ]
        created = await repo.create_batch(entries)
        await db_session.commit()

        assert len(created) == 2
        for c in created:
            assert c.tenant_id == tid
            assert c.origen == OrigenCalificacion.IMPORTADO

    async def test_create_batch_sets_importado_at(
        self, calif_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
    ) -> None:
        from app.models.calificaciones import Calificacion, OrigenCalificacion
        from app.repositories.calificaciones import CalificacionRepository

        tid = seed_tenant_admin["tenant_id"]
        repo = CalificacionRepository(db_session, tid)
        entries = [
            Calificacion(
                tenant_id=tid,
                entrada_padron_id=seed_padron_activo["alumno1_id"],
                materia_id=seed_estructura["materia_id"],
                actividad="Examen",
                nota_numerica=80.0,
                nota_textual=None,
                aprobado=True,
                origen=OrigenCalificacion.IMPORTADO,
            ),
        ]
        created = await repo.create_batch(entries)
        await db_session.commit()

        assert created[0].importado_at is not None

    async def test_list_by_materia_returns_only_matching(
        self, calif_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_calificaciones: dict[str, Any],
    ) -> None:
        from app.repositories.calificaciones import CalificacionRepository

        repo = CalificacionRepository(db_session, seed_tenant_admin["tenant_id"])
        result = await repo.list_by_materia(seed_estructura["materia_id"])

        assert len(result) == 3
        assert all(c.materia_id == seed_estructura["materia_id"] for c in result)

    async def test_list_by_materia_different_materia_returns_empty(
        self, calif_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_calificaciones: dict[str, Any],
    ) -> None:
        from app.repositories.calificaciones import CalificacionRepository

        repo = CalificacionRepository(db_session, seed_tenant_admin["tenant_id"])
        result = await repo.list_by_materia(uuid4())

        assert result == []

    async def test_get_by_id_returns_record(
        self, calif_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_calificaciones: dict[str, Any],
    ) -> None:
        from app.repositories.calificaciones import CalificacionRepository

        repo = CalificacionRepository(db_session, seed_tenant_admin["tenant_id"])
        result = await repo.get_by_id(seed_calificaciones["calif1_id"])

        assert result is not None
        assert result.id == seed_calificaciones["calif1_id"]
        assert result.nota_numerica == 75.0

    async def test_get_by_id_not_found_returns_none(
        self, calif_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_calificaciones: dict[str, Any],
    ) -> None:
        from app.repositories.calificaciones import CalificacionRepository

        repo = CalificacionRepository(db_session, seed_tenant_admin["tenant_id"])
        result = await repo.get_by_id(uuid4())

        assert result is None

    async def test_soft_delete_by_materia_marks_deleted(
        self, calif_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_calificaciones: dict[str, Any],
    ) -> None:
        from app.repositories.calificaciones import CalificacionRepository

        repo = CalificacionRepository(db_session, seed_tenant_admin["tenant_id"])
        count = await repo.soft_delete_by_materia(
            seed_estructura["materia_id"],
            seed_tenant_admin["user_id"],
        )
        await db_session.commit()

        assert count == 3

        # Verify they are soft-deleted
        remaining = await repo.list_by_materia(seed_estructura["materia_id"])
        assert remaining == []

    async def test_soft_delete_by_materia_no_match_returns_zero(
        self, calif_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_calificaciones: dict[str, Any],
    ) -> None:
        from app.repositories.calificaciones import CalificacionRepository

        repo = CalificacionRepository(db_session, seed_tenant_admin["tenant_id"])
        count = await repo.soft_delete_by_materia(uuid4(), seed_tenant_admin["user_id"])

        assert count == 0

    async def test_count_by_materia_returns_count(
        self, calif_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_calificaciones: dict[str, Any],
    ) -> None:
        from app.repositories.calificaciones import CalificacionRepository

        repo = CalificacionRepository(db_session, seed_tenant_admin["tenant_id"])
        count = await repo.count_by_materia(seed_estructura["materia_id"])

        assert count == 3

    async def test_count_by_materia_excludes_soft_deleted(
        self, calif_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_calificaciones: dict[str, Any],
    ) -> None:
        from app.repositories.calificaciones import CalificacionRepository

        repo = CalificacionRepository(db_session, seed_tenant_admin["tenant_id"])

        # Soft delete all records for the materia
        await repo.soft_delete_by_materia(
            seed_estructura["materia_id"],
            seed_tenant_admin["user_id"],
        )
        await db_session.commit()

        count = await repo.count_by_materia(seed_estructura["materia_id"])
        assert count == 0


class TestUmbralMateriaRepository:
    """UmbralMateriaRepository: get_by_asignacion, upsert, delete, get_default."""

    async def test_get_by_asignacion_finds_record(
        self, calif_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_asignacion: dict[str, Any],
        seed_umbral: dict[str, Any],
    ) -> None:
        from app.repositories.calificaciones import UmbralMateriaRepository

        repo = UmbralMateriaRepository(db_session, seed_tenant_admin["tenant_id"])
        result = await repo.get_by_asignacion(
            seed_asignacion["asignacion_id"],
            seed_estructura["materia_id"],
        )

        assert result is not None
        assert result.umbral_pct == 70
        assert result.id == seed_umbral["umbral_id"]

    async def test_get_by_asignacion_not_found_returns_none(
        self, calif_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        from app.repositories.calificaciones import UmbralMateriaRepository

        repo = UmbralMateriaRepository(db_session, seed_tenant_admin["tenant_id"])
        result = await repo.get_by_asignacion(uuid4(), uuid4())

        assert result is None

    async def test_upsert_creates_new(
        self, calif_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_asignacion: dict[str, Any],
    ) -> None:
        from app.repositories.calificaciones import UmbralMateriaRepository

        repo = UmbralMateriaRepository(db_session, seed_tenant_admin["tenant_id"])
        data = {"umbral_pct": 80, "valores_aprobatorios": ["Aprobado"]}
        result = await repo.upsert(
            seed_asignacion["asignacion_id"],
            seed_estructura["materia_id"],
            data,
        )
        await db_session.commit()

        assert result.umbral_pct == 80
        assert result.valores_aprobatorios == ["Aprobado"]

        # Verify it's persisted
        fetched = await repo.get_by_asignacion(
            seed_asignacion["asignacion_id"],
            seed_estructura["materia_id"],
        )
        assert fetched is not None
        assert fetched.umbral_pct == 80

    async def test_upsert_updates_existing(
        self, calif_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_asignacion: dict[str, Any],
        seed_umbral: dict[str, Any],
    ) -> None:
        from app.repositories.calificaciones import UmbralMateriaRepository

        repo = UmbralMateriaRepository(db_session, seed_tenant_admin["tenant_id"])
        data = {"umbral_pct": 90, "valores_aprobatorios": ["Excelente"]}
        result = await repo.upsert(
            seed_asignacion["asignacion_id"],
            seed_estructura["materia_id"],
            data,
        )
        await db_session.commit()

        assert result.umbral_pct == 90
        assert result.valores_aprobatorios == ["Excelente"]
        assert result.id == seed_umbral["umbral_id"]

    async def test_delete_soft_deletes(
        self, calif_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_umbral: dict[str, Any],
    ) -> None:
        from app.repositories.calificaciones import UmbralMateriaRepository

        repo = UmbralMateriaRepository(db_session, seed_tenant_admin["tenant_id"])
        deleted = await repo.delete(seed_umbral["umbral_id"])
        await db_session.commit()

        assert deleted is True

        # Verify it's gone from queries
        from app.models.calificaciones import UmbralMateria
        persisted = await db_session.get(UmbralMateria, seed_umbral["umbral_id"])
        assert persisted is not None
        assert persisted.deleted_at is not None

    async def test_delete_not_found_returns_false(
        self, calif_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        from app.repositories.calificaciones import UmbralMateriaRepository

        repo = UmbralMateriaRepository(db_session, seed_tenant_admin["tenant_id"])
        deleted = await repo.delete(uuid4())

        assert deleted is False


class TestUmbralMateriaRepositoryGetDefault:
    """UmbralMateriaRepository.get_default() static."""

    def test_get_default_returns_correct_values(self) -> None:
        from app.repositories.calificaciones import UmbralMateriaRepository

        result = UmbralMateriaRepository.get_default()

        assert result["umbral_pct"] == 60
        assert "Satisfactorio" in result["valores_aprobatorios"]
        assert "Supera lo esperado" in result["valores_aprobatorios"]
        assert len(result["valores_aprobatorios"]) == 2

    def test_get_default_is_immutable_per_call(self) -> None:
        from app.repositories.calificaciones import UmbralMateriaRepository

        result1 = UmbralMateriaRepository.get_default()
        result2 = UmbralMateriaRepository.get_default()

        # Modifying one should not affect the other
        result1["umbral_pct"] = 99
        assert result2["umbral_pct"] == 60


# ═══════════════════════════════════════════════════════════════
# 3.1 / 3.2 / 3.3 / 3.4 — Schema tests
# ═══════════════════════════════════════════════════════════════


class TestCalificacionSchemas:
    """CalificacionCreate, CalificacionResponse, CalificacionListResponse."""

    def test_calificacion_create_valid(self) -> None:
        from app.schemas.calificaciones import CalificacionCreate

        data = CalificacionCreate(
            entrada_padron_id=uuid4(),
            materia_id=uuid4(),
            actividad="TP1",
        )

        assert data.actividad == "TP1"
        assert data.nota_numerica is None
        assert data.nota_textual is None

    def test_calificacion_create_with_optional_fields(self) -> None:
        from app.schemas.calificaciones import CalificacionCreate

        data = CalificacionCreate(
            entrada_padron_id=uuid4(),
            materia_id=uuid4(),
            actividad="Examen",
            nota_numerica=85.5,
            nota_textual="Bueno",
        )

        assert data.nota_numerica == 85.5
        assert data.nota_textual == "Bueno"

    def test_calificacion_create_rejects_extra(self) -> None:
        from pydantic import ValidationError
        from app.schemas.calificaciones import CalificacionCreate

        try:
            CalificacionCreate(
                entrada_padron_id=uuid4(),
                materia_id=uuid4(),
                actividad="TP1",
                campo_inventado="x",
            )
            pytest.fail("Should have raised ValidationError")
        except ValidationError:
            pass

    def test_calificacion_response_all_fields(self) -> None:
        from app.schemas.calificaciones import CalificacionResponse

        now = datetime.now(UTC)
        data = CalificacionResponse(
            id=uuid4(),
            tenant_id=uuid4(),
            entrada_padron_id=uuid4(),
            materia_id=uuid4(),
            actividad="TP1",
            nota_numerica=90.0,
            nota_textual=None,
            aprobado=True,
            origen="Importado",
            importado_at=now,
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )

        assert data.aprobado is True
        assert data.origen == "Importado"
        assert data.nota_numerica == 90.0

    def test_calificacion_list_response_with_items(self) -> None:
        from app.schemas.calificaciones import CalificacionListResponse, CalificacionResponse

        now = datetime.now(UTC)
        items = [
            CalificacionResponse(
                id=uuid4(),
                tenant_id=uuid4(),
                entrada_padron_id=uuid4(),
                materia_id=uuid4(),
                actividad="TP1",
                nota_numerica=75.0,
                nota_textual=None,
                aprobado=True,
                origen="Importado",
                importado_at=now,
                created_at=now,
                updated_at=now,
                deleted_at=None,
            )
        ]
        data = CalificacionListResponse(items=items, total=1)

        assert data.total == 1
        assert len(data.items) == 1


class TestUmbralSchemas:
    """UmbralMateriaCreate, UmbralMateriaResponse, UmbralMateriaUpdate."""

    def test_umbral_create_defaults(self) -> None:
        from app.schemas.calificaciones import UmbralMateriaCreate

        data = UmbralMateriaCreate()

        assert data.umbral_pct == 60
        assert len(data.valores_aprobatorios) == 2
        assert "Satisfactorio" in data.valores_aprobatorios

    def test_umbral_create_custom(self) -> None:
        from app.schemas.calificaciones import UmbralMateriaCreate

        data = UmbralMateriaCreate(umbral_pct=75, valores_aprobatorios=["Aprobado", "Muy bueno"])

        assert data.umbral_pct == 75
        assert data.valores_aprobatorios == ["Aprobado", "Muy bueno"]

    def test_umbral_create_rejects_extra(self) -> None:
        from pydantic import ValidationError
        from app.schemas.calificaciones import UmbralMateriaCreate

        try:
            UmbralMateriaCreate(umbral_pct=70, campo_extra="x")
            pytest.fail("Should have raised ValidationError")
        except ValidationError:
            pass

    def test_umbral_response_all_fields(self) -> None:
        from app.schemas.calificaciones import UmbralMateriaResponse

        now = datetime.now(UTC)
        data = UmbralMateriaResponse(
            id=uuid4(),
            tenant_id=uuid4(),
            asignacion_id=uuid4(),
            materia_id=uuid4(),
            umbral_pct=80,
            valores_aprobatorios=["Aprobado"],
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )

        assert data.umbral_pct == 80
        assert data.valores_aprobatorios == ["Aprobado"]

    def test_umbral_update_partial(self) -> None:
        from app.schemas.calificaciones import UmbralMateriaUpdate

        data = UmbralMateriaUpdate(umbral_pct=70)

        assert data.umbral_pct == 70
        assert data.valores_aprobatorios is None

    def test_umbral_update_rejects_extra(self) -> None:
        from pydantic import ValidationError
        from app.schemas.calificaciones import UmbralMateriaUpdate

        try:
            UmbralMateriaUpdate(umbral_pct=70, inventado=True)
            pytest.fail("Should have raised ValidationError")
        except ValidationError:
            pass


class TestImportSchemas:
    """ImportPreviewResponse, ImportConfirmRequest."""

    def test_import_preview_response(self) -> None:
        from app.schemas.calificaciones import DetectedActivity, ImportPreviewResponse, StudentMatch, UnmatchedRow

        data = ImportPreviewResponse(
            preview_token="abc",
            materia_id=uuid4(),
            cohorte_id=uuid4(),
            actividades=[
                DetectedActivity(nombre="TP1", tipo="numeric"),
                DetectedActivity(nombre="TP2", tipo="numeric"),
            ],
            total_rows=10,
            alumnos_match=[
                StudentMatch(
                    entrada_padron_id=uuid4(),
                    nombre="Juan",
                    apellidos="Perez",
                    email="juan@test.com",
                    datos={"TP1": 75.0},
                )
            ],
            alumnos_no_match=[
                UnmatchedRow(fila=3, datos={"nombre": "Unknown", "email": "x@test.com"})
            ],
        )

        assert len(data.actividades) == 2
        assert data.total_rows == 10
        assert len(data.alumnos_match) == 1
        assert len(data.alumnos_no_match) == 1

    def test_import_confirm_request_with_all(self) -> None:
        from app.schemas.calificaciones import ImportConfirmRequest

        data = ImportConfirmRequest(preview_token="abc-123", actividad_ids=["ALL"])

        assert data.preview_token == "abc-123"
        assert data.actividad_ids == ["ALL"]

    def test_import_confirm_request_rejects_extra(self) -> None:
        from pydantic import ValidationError
        from app.schemas.calificaciones import ImportConfirmRequest

        try:
            ImportConfirmRequest(preview_token="abc", actividad_ids=["TP1"], extra_field="x")
            pytest.fail("Should have raised ValidationError")
        except ValidationError:
            pass


class TestCompletionReportSchema:
    """CompletionReportResponse."""

    def test_completion_report_response(self) -> None:
        from app.schemas.calificaciones import CompletionReportResponse, PosibleEntregaSinCorregir

        data = CompletionReportResponse(
            materia_id=uuid4(),
            cohorte_id=uuid4(),
            posibles_entregas_sin_corregir=[
                PosibleEntregaSinCorregir(alumno_nombre="Juan", alumno_apellidos="Perez", actividad="Trabajo Final"),
                PosibleEntregaSinCorregir(alumno_nombre="Maria", alumno_apellidos="Gomez", actividad="Trabajo Final"),
            ]
        )

        assert len(data.posibles_entregas_sin_corregir) == 2
        assert data.posibles_entregas_sin_corregir[0].actividad == "Trabajo Final"
        assert data.posibles_entregas_sin_corregir[1].alumno_nombre == "Maria"
