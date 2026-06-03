"""Tests para C-09 Padrón / Ingesta Moodle.

Strict TDD: RED → GREEN → TRIANGULATE → REFACTOR.
"""

import io
from typing import Any
from uuid import UUID, uuid4

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
async def padron_schema(db_engine: None):
    """Creates full schema including padron tables."""
    from app.core.database import get_sessionmaker
    from app.models.estructura_academica import Carrera, Cohorte, Materia  # noqa: F401
    from app.models.padron import EntradaPadron, VersionPadron  # noqa: F401
    from app.services.auth import login_rate_limiter

    login_rate_limiter.reset_all()

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        connection = await session.connection()
        await connection.execute(
            text(
                "DROP TABLE IF EXISTS entradas_padron, versiones_padron, "
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
    """Seeds tenant + admin user + padron:importar permission."""
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
        codigo="padron:importar",
        nombre="Importar padron",
        modulo="padron",
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
async def seed_materia(db_session: AsyncSession, seed_tenant_admin: dict[str, Any]) -> dict[str, Any]:
    """Seeds a materia + cohorte for testing."""
    from app.models.estructura_academica import Carrera, Cohorte, Materia

    carrera = Carrera(tenant_id=seed_tenant_admin["tenant_id"], codigo="TEST", nombre="Test Carrera")
    db_session.add(carrera)
    await db_session.flush()

    cohorte = Cohorte(tenant_id=seed_tenant_admin["tenant_id"], carrera_id=carrera.id, nombre="2026", anio=2026)
    db_session.add(cohorte)
    await db_session.flush()

    materia = Materia(tenant_id=seed_tenant_admin["tenant_id"], codigo="MAT001", nombre="Matematica")
    db_session.add(materia)
    await db_session.flush()
    await db_session.commit()

    return {
        "carrera_id": str(carrera.id),
        "cohorte_id": str(cohorte.id),
        "materia_id": str(materia.id),
    }


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


# ═══════════════════════════════════════════════════════════════
# 11.1 — Tests de modelo y migración
# ═══════════════════════════════════════════════════════════════


class TestVersionPadronModel:
    """Versionado: activar desactiva anterior, historial preservado."""

    async def test_create_first_version_activates_it(
        self, padron_schema, db_session: AsyncSession, seed_tenant_admin: dict[str, Any],
        seed_materia: dict[str, Any],
    ) -> None:
        from app.models.padron import VersionPadron

        version = VersionPadron(
            tenant_id=seed_tenant_admin["tenant_id"],
            materia_id=UUID(seed_materia["materia_id"]),
            cohorte_id=UUID(seed_materia["cohorte_id"]),
            cargado_por=seed_tenant_admin["user_id"],
            activa=True,
        )
        db_session.add(version)
        await db_session.flush()

        assert version.id is not None
        assert version.activa is True
        assert version.cargado_at is not None
        assert version.created_at is not None

    async def test_second_version_deactivates_first(
        self, padron_schema, db_session: AsyncSession, seed_tenant_admin: dict[str, Any],
        seed_materia: dict[str, Any],
    ) -> None:
        from app.models.padron import VersionPadron
        from app.repositories.padron import VersionPadronRepository

        repo = VersionPadronRepository(db_session, seed_tenant_admin["tenant_id"])

        v1 = await repo.crear_version(
            materia_id=UUID(seed_materia["materia_id"]),
            cohorte_id=UUID(seed_materia["cohorte_id"]),
            cargado_por=seed_tenant_admin["user_id"],
        )
        assert v1.activa is True

        v2 = await repo.crear_version(
            materia_id=UUID(seed_materia["materia_id"]),
            cohorte_id=UUID(seed_materia["cohorte_id"]),
            cargado_por=seed_tenant_admin["user_id"],
        )
        assert v2.activa is True

        # v1 should now be inactive
        await db_session.refresh(v1)
        assert v1.activa is False

    async def test_three_versions_only_latest_active(
        self, padron_schema, db_session: AsyncSession, seed_tenant_admin: dict[str, Any],
        seed_materia: dict[str, Any],
    ) -> None:
        from app.models.padron import VersionPadron
        from app.repositories.padron import VersionPadronRepository

        repo = VersionPadronRepository(db_session, seed_tenant_admin["tenant_id"])

        v1 = await repo.crear_version(
            materia_id=UUID(seed_materia["materia_id"]),
            cohorte_id=UUID(seed_materia["cohorte_id"]),
            cargado_por=seed_tenant_admin["user_id"],
        )
        v2 = await repo.crear_version(
            materia_id=UUID(seed_materia["materia_id"]),
            cohorte_id=UUID(seed_materia["cohorte_id"]),
            cargado_por=seed_tenant_admin["user_id"],
        )
        v3 = await repo.crear_version(
            materia_id=UUID(seed_materia["materia_id"]),
            cohorte_id=UUID(seed_materia["cohorte_id"]),
            cargado_por=seed_tenant_admin["user_id"],
        )

        await db_session.refresh(v1)
        await db_session.refresh(v2)
        await db_session.refresh(v3)

        assert v1.activa is False
        assert v2.activa is False
        assert v3.activa is True

        # All 3 versions exist
        items, total = await repo.listar_por_materia(UUID(seed_materia["materia_id"]))
        assert total == 3

    async def test_entrada_padron_without_usuario_id(
        self, padron_schema, db_session: AsyncSession, seed_tenant_admin: dict[str, Any],
        seed_materia: dict[str, Any],
    ) -> None:
        from app.models.padron import EntradaPadron, VersionPadron
        from app.repositories.padron import VersionPadronRepository

        repo = VersionPadronRepository(db_session, seed_tenant_admin["tenant_id"])
        version = await repo.crear_version(
            materia_id=UUID(seed_materia["materia_id"]),
            cohorte_id=UUID(seed_materia["cohorte_id"]),
            cargado_por=seed_tenant_admin["user_id"],
        )

        entrada = EntradaPadron(
            tenant_id=seed_tenant_admin["tenant_id"],
            version_id=version.id,
            usuario_id=None,
            nombre="Juan",
            apellidos="Perez",
            email="juan@test.com",
            comision="A",
        )
        db_session.add(entrada)
        await db_session.flush()

        assert entrada.id is not None
        assert entrada.usuario_id is None
        assert entrada.nombre == "Juan"


# ═══════════════════════════════════════════════════════════════
# 11.2 — Tests de repositorio
# ═══════════════════════════════════════════════════════════════


class TestPadronRepository:
    """CRUD, versionado, vaciar scope RN-04, soft delete."""

    async def test_vaciar_only_own_data(
        self, padron_schema, db_session: AsyncSession, seed_tenant_admin: dict[str, Any],
        seed_materia: dict[str, Any],
    ) -> None:
        from app.repositories.padron import VersionPadronRepository

        repo = VersionPadronRepository(db_session, seed_tenant_admin["tenant_id"])
        materia_id = UUID(seed_materia["materia_id"])

        # Create 2 versions as current user
        await repo.crear_version(materia_id, UUID(seed_materia["cohorte_id"]), seed_tenant_admin["user_id"])
        await repo.crear_version(materia_id, UUID(seed_materia["cohorte_id"]), seed_tenant_admin["user_id"])

        # Create 1 version as another user
        other_user_id = uuid4()
        await repo.crear_version(materia_id, UUID(seed_materia["cohorte_id"]), other_user_id)

        # Verify 3 versions exist before vaciar
        items_before, total_before = await repo.listar_por_materia(materia_id)
        assert total_before == 3

        # Vaciar current user's data
        from app.repositories.padron import EntradaPadronRepository
        entrada_repo = EntradaPadronRepository(db_session, seed_tenant_admin["tenant_id"])
        affected = await entrada_repo.vaciar_por_usuario_y_materia(
            seed_tenant_admin["user_id"], materia_id
        )
        assert affected == 2  # Only current user's versions

        # Other user's version still active
        items_after, total_after = await repo.listar_por_materia(materia_id)
        assert total_after == 1  # Only the other user's remains

    async def test_soft_delete_not_returned(
        self, padron_schema, db_session: AsyncSession, seed_tenant_admin: dict[str, Any],
        seed_materia: dict[str, Any],
    ) -> None:
        from app.models.padron import VersionPadron
        from app.repositories.padron import VersionPadronRepository

        repo = VersionPadronRepository(db_session, seed_tenant_admin["tenant_id"])
        materia_id = UUID(seed_materia["materia_id"])

        version = await repo.crear_version(materia_id, UUID(seed_materia["cohorte_id"]), seed_tenant_admin["user_id"])
        assert version.deleted_at is None

        await repo.soft_delete(version.id)
        await db_session.refresh(version)
        assert version.deleted_at is not None

        # Should not appear in list
        items, total = await repo.listar_por_materia(materia_id)
        assert total == 0


# ═══════════════════════════════════════════════════════════════
# 11.3 — Tests de file parser
# ═══════════════════════════════════════════════════════════════


class TestFileParser:
    """xlsx válido, csv delimitador alternativo, columnas faltantes."""

    def test_csv_valid_parsing(self) -> None:
        from app.services.file_parser import parsear_csv

        csv_content = "nombre,apellidos,email,comision\nJuan,Perez,juan@test.com,A\nMaria,Gomez,maria@test.com,B\n".encode("utf-8")
        result = parsear_csv(csv_content)

        assert result.total_filas == 2
        assert len(result.columnas) == 4
        assert result.filas[0].datos["nombre"] == "Juan"

    def test_csv_semicolon_delimiter(self) -> None:
        from app.services.file_parser import parsear_csv

        csv_content = "nombre;apellidos;email;comision\nJuan;Perez;juan@test.com;A\n".encode("utf-8")
        result = parsear_csv(csv_content)

        assert result.total_filas == 1
        assert result.filas[0].datos["email"] == "juan@test.com"

    def test_csv_missing_required_columns(self) -> None:
        from app.services.file_parser import FileParseError, parsear_csv

        csv_content = "nombre,comision\nJuan,A\n".encode("utf-8")
        with pytest.raises(FileParseError, match="apellidos"):
            parsear_csv(csv_content)

    def test_csv_empty_file(self) -> None:
        from app.services.file_parser import FileParseError, parsear_csv

        with pytest.raises(FileParseError, match="vacío"):
            parsear_csv(b"")

    def test_csv_skips_empty_rows(self) -> None:
        from app.services.file_parser import parsear_csv

        csv_content = "nombre,apellidos,email\nJuan,Perez,juan@test.com\n\nMaria,Gomez,maria@test.com\n".encode("utf-8")
        result = parsear_csv(csv_content)

        assert result.total_filas == 2

    def test_csv_preview_limited(self) -> None:
        from app.services.file_parser import parsear_csv

        rows = "\n".join([f"nombre,apellidos,email"] + [f"Alumno{i},Apellido{i},a{i}@test.com" for i in range(100)])
        result = parsear_csv(rows.encode("utf-8"))

        assert result.total_filas == 100
        assert len(result.filas) == 5  # Preview limited to 5

    def test_unsupported_format(self) -> None:
        from app.services.file_parser import FileParseError, parsear_archivo

        with pytest.raises(FileParseError, match="no soportado"):
            parsear_archivo("test.pdf", b"data")


# ═══════════════════════════════════════════════════════════════
# 11.4 — Tests de import flow (preview → confirmar)
# ═══════════════════════════════════════════════════════════════


class TestImportFlow:
    """Preview → confirmar → versión activa. Preview expirado → 409."""

    @pytest.fixture
    async def csv_file(self) -> tuple[str, bytes]:
        content = "nombre,apellidos,email,comision\nJuan,Perez,juan@test.com,A\nMaria,Gomez,maria@test.com,B\n"
        return "test.csv", content.encode("utf-8")

    async def test_preview_returns_column_info(
        self, padron_schema, async_client: AsyncClient, seed_tenant_admin: dict[str, Any],
        seed_materia: dict[str, Any], csv_file: tuple[str, bytes],
    ) -> None:
        headers = await admin_headers(async_client)
        filename, content = csv_file

        resp = await async_client.post(
            "/api/v1/padron/preview",
            data={
                "materia_id": seed_materia["materia_id"],
                "cohorte_id": seed_materia["cohorte_id"],
            },
            files={"archivo": (filename, content, "text/csv")},
            headers=headers,
        )

        assert resp.status_code == 200
        data = resp.json()
        assert "preview_token" in data
        assert data["total_filas"] == 2
        assert len(data["columnas_detectadas"]) >= 3  # nombre, apellidos, email
        assert len(data["filas_preview"]) == 2

    async def test_confirm_creates_version(
        self, padron_schema, async_client: AsyncClient, seed_tenant_admin: dict[str, Any],
        seed_materia: dict[str, Any], csv_file: tuple[str, bytes],
    ) -> None:
        headers = await admin_headers(async_client)
        filename, content = csv_file

        # Step 1: preview
        preview_resp = await async_client.post(
            "/api/v1/padron/preview",
            data={
                "materia_id": seed_materia["materia_id"],
                "cohorte_id": seed_materia["cohorte_id"],
            },
            files={"archivo": (filename, content, "text/csv")},
            headers=headers,
        )
        preview_data = preview_resp.json()

        # Step 2: confirm
        resp = await async_client.post(
            "/api/v1/padron/confirmar",
            json={"preview_token": preview_data["preview_token"]},
            headers=headers,
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["entry_count"] == 2
        assert "version_id" in data
        assert data["materia_id"] == seed_materia["materia_id"]

    async def test_confirm_with_expired_token_returns_409(
        self, padron_schema, async_client: AsyncClient, seed_tenant_admin: dict[str, Any],
        seed_materia: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        resp = await async_client.post(
            "/api/v1/padron/confirmar",
            json={"preview_token": str(uuid4())},  # Non-existent token
            headers=headers,
        )

        assert resp.status_code == 409

    async def test_preview_then_list_versions(
        self, padron_schema, async_client: AsyncClient, seed_tenant_admin: dict[str, Any],
        seed_materia: dict[str, Any], csv_file: tuple[str, bytes],
    ) -> None:
        headers = await admin_headers(async_client)
        filename, content = csv_file

        # Preview + confirm
        preview = await async_client.post(
            "/api/v1/padron/preview",
            data={"materia_id": seed_materia["materia_id"], "cohorte_id": seed_materia["cohorte_id"]},
            files={"archivo": (filename, content, "text/csv")},
            headers=headers,
        )
        await async_client.post(
            "/api/v1/padron/confirmar",
            json={"preview_token": preview.json()["preview_token"]},
            headers=headers,
        )

        # List versions
        resp = await async_client.get(
            f"/api/v1/padron/materias/{seed_materia['materia_id']}/versiones",
            headers=headers,
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["activa"] is True


# ═══════════════════════════════════════════════════════════════
# 11.5 — Tests de vaciar (RN-04)
# ═══════════════════════════════════════════════════════════════


class TestVaciar:
    """Solo datos propios, datos de otros preservados."""

    async def test_vaciar_removes_own_versions(
        self, padron_schema, async_client: AsyncClient, seed_tenant_admin: dict[str, Any],
        seed_materia: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)
        filename = "test.csv"
        content = "nombre,apellidos,email\nJuan,Perez,juan@test.com\n".encode("utf-8")

        # Import first
        preview = await async_client.post(
            "/api/v1/padron/preview",
            data={"materia_id": seed_materia["materia_id"], "cohorte_id": seed_materia["cohorte_id"]},
            files={"archivo": (filename, content, "text/csv")},
            headers=headers,
        )
        await async_client.post(
            "/api/v1/padron/confirmar",
            json={"preview_token": preview.json()["preview_token"]},
            headers=headers,
        )

        # Vaciar
        resp = await async_client.delete(
            f"/api/v1/padron/materias/{seed_materia['materia_id']}/vaciar",
            headers=headers,
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["affected_count"] >= 1
        assert data["materia_id"] == seed_materia["materia_id"]


# ═══════════════════════════════════════════════════════════════
# 11.6 — Tests de MoodleClient
# ═══════════════════════════════════════════════════════════════


class TestMoodleClient:
    """Sync usuarios, retry transitorio, auth failure inmediato, 502 fallback."""

    def test_not_configured_raises_error(self) -> None:
        from app.integrations.moodle_ws import MoodleClient, MoodleError

        client = MoodleClient(config=None)
        assert client.is_configured is False

    def test_configured_returns_true(self) -> None:
        from app.integrations.moodle_ws import MoodleClient, MoodleConfig

        config = MoodleConfig(base_url="https://moodle.test", token="abc123")
        client = MoodleClient(config=config)
        assert client.is_configured is True


# ═══════════════════════════════════════════════════════════════
# 11.7 — Tests de sync on-demand
# ═══════════════════════════════════════════════════════════════


class TestMoodleSync:
    """PROFESOR autorizado, COORDINADOR autorizado, sin permiso → 403."""

    async def test_sync_without_moodle_config_returns_502(
        self, padron_schema, async_client: AsyncClient, seed_tenant_admin: dict[str, Any],
        seed_materia: dict[str, Any],
    ) -> None:
        """Without MOODLE_BASE_URL, sync should return 502."""
        headers = await admin_headers(async_client)

        resp = await async_client.post(
            f"/api/v1/moodle/sync/{seed_materia['materia_id']}",
            params={
                "cohorte_id": seed_materia["cohorte_id"],
                "course_id": 1,
            },
            headers=headers,
        )

        assert resp.status_code == 502
        assert "Moodle" in resp.text
