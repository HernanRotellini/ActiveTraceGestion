"""Tests de API para C-17 Programas y Fechas Académicas."""

from datetime import date
from typing import Any
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password
from tests.test_c17_services import (
    crear_carrera,
    crear_cohorte,
    crear_materia,
    c17_schema,  # noqa: F401
)


@pytest.fixture
async def c17_api_context(db_session: AsyncSession, c17_schema: None) -> dict[str, Any]:
    from app.models.auth import AuthUser
    from app.models.rbac import Permiso, Rol, RolPermiso
    from app.models.tenant import Tenant

    tenant = Tenant(name="Tenant C17 API", code="c17-api")
    other_tenant = Tenant(name="Otro Tenant C17 API", code="c17-api-otro")
    db_session.add_all([tenant, other_tenant])
    await db_session.flush()

    admin = AuthUser(
        tenant_id=tenant.id,
        email="admin-c17@example.com",
        password_hash=hash_password("password"),
        roles=["ADMIN"],
        is_active=True,
    )
    no_permission = AuthUser(
        tenant_id=tenant.id,
        email="sin-permiso-c17@example.com",
        password_hash=hash_password("password"),
        roles=["LECTOR"],
        is_active=True,
    )
    db_session.add_all([admin, no_permission])
    await db_session.flush()

    rol = Rol(tenant_id=tenant.id, codigo="ADMIN", nombre="Admin")
    permiso = Permiso(
        tenant_id=tenant.id,
        codigo="estructura:gestionar",
        nombre="Gestionar estructura",
        modulo="estructura",
        accion="gestionar",
    )
    db_session.add_all([rol, permiso])
    await db_session.flush()
    db_session.add(
        RolPermiso(
            tenant_id=tenant.id,
            rol_id=rol.id,
            permiso_id=permiso.id,
            habilitado=True,
            alcance="global",
        )
    )

    carrera_id = await crear_carrera(db_session, tenant.id)
    cohorte_id = await crear_cohorte(db_session, tenant.id, carrera_id)
    materia_id = await crear_materia(db_session, tenant.id)

    other_carrera_id = await crear_carrera(db_session, other_tenant.id, codigo="CAR-OTHER")
    other_cohorte_id = await crear_cohorte(db_session, other_tenant.id, other_carrera_id, nombre="Other-Coh")
    other_materia_id = await crear_materia(db_session, other_tenant.id, codigo="MAT-OTHER")
    await db_session.commit()

    from app.core.config import Settings

    settings = Settings(_env_file=None)  # type: ignore[call-arg]
    admin_token = create_access_token(
        user_id=admin.id,
        tenant_id=tenant.id,
        roles=admin.roles,
        settings=settings,
    )
    no_perm_token = create_access_token(
        user_id=no_permission.id,
        tenant_id=tenant.id,
        roles=no_permission.roles,
        settings=settings,
    )

    return {
        "tenant_code": tenant.code,
        "admin_token": admin_token,
        "no_perm_token": no_perm_token,
        "admin_id": admin.id,
        "carrera_id": carrera_id,
        "cohorte_id": cohorte_id,
        "materia_id": materia_id,
        "other_carrera_id": other_carrera_id,
        "other_cohorte_id": other_cohorte_id,
        "other_materia_id": other_materia_id,
    }


def admin_headers(context: dict[str, Any]) -> dict[str, str]:
    return {"Authorization": f"Bearer {context['admin_token']}"}


def no_perm_headers(context: dict[str, Any]) -> dict[str, str]:
    return {"Authorization": f"Bearer {context['no_perm_token']}"}


class TestProgramasAPI:
    async def test_create_programa_returns_201(
        self,
        async_client: AsyncClient,
        c17_api_context: dict[str, Any],
    ) -> None:
        headers = admin_headers(c17_api_context)
        response = await async_client.post(
            "/api/programas",
            json={
                "materia_id": str(c17_api_context["materia_id"]),
                "carrera_id": str(c17_api_context["carrera_id"]),
                "cohorte_id": str(c17_api_context["cohorte_id"]),
                "titulo": "Programa Analítico 2026",
                "referencia_archivo": "/files/programa.pdf",
            },
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["titulo"] == "Programa Analítico 2026"
        assert data["materia_id"] == str(c17_api_context["materia_id"])
        assert "id" in data

    async def test_create_programa_duplicate_returns_409(
        self,
        async_client: AsyncClient,
        c17_api_context: dict[str, Any],
    ) -> None:
        headers = admin_headers(c17_api_context)
        payload = {
            "materia_id": str(c17_api_context["materia_id"]),
            "carrera_id": str(c17_api_context["carrera_id"]),
            "cohorte_id": str(c17_api_context["cohorte_id"]),
            "titulo": "Duplicated",
            "referencia_archivo": "/files/d1.pdf",
        }
        r1 = await async_client.post("/api/programas", json=payload, headers=headers)
        assert r1.status_code == 201
        r2 = await async_client.post("/api/programas", json=payload, headers=headers)
        assert r2.status_code == 409

    async def test_create_programa_cross_tenant_returns_404(
        self,
        async_client: AsyncClient,
        c17_api_context: dict[str, Any],
    ) -> None:
        headers = admin_headers(c17_api_context)
        response = await async_client.post(
            "/api/programas",
            json={
                "materia_id": str(c17_api_context["other_materia_id"]),
                "carrera_id": str(c17_api_context["other_carrera_id"]),
                "cohorte_id": str(c17_api_context["other_cohorte_id"]),
                "titulo": "Cross Tenant",
                "referencia_archivo": "/files/cross.pdf",
            },
            headers=headers,
        )
        assert response.status_code == 404

    async def test_create_programa_missing_permission_returns_403(
        self,
        async_client: AsyncClient,
        c17_api_context: dict[str, Any],
    ) -> None:
        headers = no_perm_headers(c17_api_context)
        response = await async_client.post(
            "/api/programas",
            json={
                "materia_id": str(c17_api_context["materia_id"]),
                "carrera_id": str(c17_api_context["carrera_id"]),
                "cohorte_id": str(c17_api_context["cohorte_id"]),
                "titulo": "No Auth",
                "referencia_archivo": "/files/na.pdf",
            },
            headers=headers,
        )
        assert response.status_code == 403

    async def test_create_programa_invalid_payload_returns_422(
        self,
        async_client: AsyncClient,
        c17_api_context: dict[str, Any],
    ) -> None:
        headers = admin_headers(c17_api_context)
        response = await async_client.post(
            "/api/programas",
            json={
                "materia_id": "not-a-uuid",
            },
            headers=headers,
        )
        assert response.status_code == 422

    async def test_create_programa_extra_fields_rejected_returns_422(
        self,
        async_client: AsyncClient,
        c17_api_context: dict[str, Any],
    ) -> None:
        headers = admin_headers(c17_api_context)
        response = await async_client.post(
            "/api/programas",
            json={
                "materia_id": str(c17_api_context["materia_id"]),
                "carrera_id": str(c17_api_context["carrera_id"]),
                "cohorte_id": str(c17_api_context["cohorte_id"]),
                "titulo": "Extra",
                "referencia_archivo": "/files/e.pdf",
                "extra_field": "should be rejected",
            },
            headers=headers,
        )
        assert response.status_code == 422

    async def test_list_programas_returns_200(
        self,
        async_client: AsyncClient,
        c17_api_context: dict[str, Any],
    ) -> None:
        headers = admin_headers(c17_api_context)
        response = await async_client.get("/api/programas", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_get_programa_returns_200(
        self,
        async_client: AsyncClient,
        c17_api_context: dict[str, Any],
    ) -> None:
        headers = admin_headers(c17_api_context)
        created = await async_client.post(
            "/api/programas",
            json={
                "materia_id": str(c17_api_context["materia_id"]),
                "carrera_id": str(c17_api_context["carrera_id"]),
                "cohorte_id": str(c17_api_context["cohorte_id"]),
                "titulo": "Get Test",
                "referencia_archivo": "/files/get.pdf",
            },
            headers=headers,
        )
        programa_id = created.json()["id"]
        response = await async_client.get(f"/api/programas/{programa_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["titulo"] == "Get Test"

    async def test_get_programa_not_found_returns_404(
        self,
        async_client: AsyncClient,
        c17_api_context: dict[str, Any],
    ) -> None:
        headers = admin_headers(c17_api_context)
        response = await async_client.get(f"/api/programas/{uuid4()}", headers=headers)
        assert response.status_code == 404

    async def test_update_programa_returns_200(
        self,
        async_client: AsyncClient,
        c17_api_context: dict[str, Any],
    ) -> None:
        headers = admin_headers(c17_api_context)
        created = await async_client.post(
            "/api/programas",
            json={
                "materia_id": str(c17_api_context["materia_id"]),
                "carrera_id": str(c17_api_context["carrera_id"]),
                "cohorte_id": str(c17_api_context["cohorte_id"]),
                "titulo": "Before Update",
                "referencia_archivo": "/files/before.pdf",
            },
            headers=headers,
        )
        programa_id = created.json()["id"]
        response = await async_client.put(
            f"/api/programas/{programa_id}",
            json={"titulo": "After Update", "referencia_archivo": "/files/after.pdf"},
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json()["titulo"] == "After Update"

    async def test_delete_programa_returns_204(
        self,
        async_client: AsyncClient,
        c17_api_context: dict[str, Any],
    ) -> None:
        headers = admin_headers(c17_api_context)
        created = await async_client.post(
            "/api/programas",
            json={
                "materia_id": str(c17_api_context["materia_id"]),
                "carrera_id": str(c17_api_context["carrera_id"]),
                "cohorte_id": str(c17_api_context["cohorte_id"]),
                "titulo": "To Delete API",
                "referencia_archivo": "/files/del.pdf",
            },
            headers=headers,
        )
        programa_id = created.json()["id"]
        response = await async_client.delete(f"/api/programas/{programa_id}", headers=headers)
        assert response.status_code == 204


class TestFechasAcademicasAPI:
    async def test_create_fecha_returns_201(
        self,
        async_client: AsyncClient,
        c17_api_context: dict[str, Any],
    ) -> None:
        headers = admin_headers(c17_api_context)
        response = await async_client.post(
            "/api/fechas-academicas",
            json={
                "materia_id": str(c17_api_context["materia_id"]),
                "cohorte_id": str(c17_api_context["cohorte_id"]),
                "tipo": "Parcial",
                "numero": 1,
                "periodo": "2026-1C",
                "fecha": "2026-05-15",
                "titulo": "Primer Parcial",
            },
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["titulo"] == "Primer Parcial"
        assert data["tipo"] == "Parcial"

    async def test_create_fecha_duplicate_returns_409(
        self,
        async_client: AsyncClient,
        c17_api_context: dict[str, Any],
    ) -> None:
        headers = admin_headers(c17_api_context)
        payload = {
            "materia_id": str(c17_api_context["materia_id"]),
            "cohorte_id": str(c17_api_context["cohorte_id"]),
            "tipo": "TP",
            "numero": 1,
            "periodo": "2026-1C",
            "fecha": "2026-06-01",
            "titulo": "TP Duplicate",
        }
        r1 = await async_client.post("/api/fechas-academicas", json=payload, headers=headers)
        assert r1.status_code == 201
        r2 = await async_client.post("/api/fechas-academicas", json=payload, headers=headers)
        assert r2.status_code == 409

    async def test_create_fecha_cross_tenant_rejected(
        self,
        async_client: AsyncClient,
        c17_api_context: dict[str, Any],
    ) -> None:
        headers = admin_headers(c17_api_context)
        response = await async_client.post(
            "/api/fechas-academicas",
            json={
                "materia_id": str(c17_api_context["other_materia_id"]),
                "cohorte_id": str(c17_api_context["other_cohorte_id"]),
                "tipo": "Parcial",
                "numero": 1,
                "periodo": "2026-1C",
                "fecha": "2026-05-15",
                "titulo": "Cross",
            },
            headers=headers,
        )
        assert response.status_code == 404

    async def test_create_fecha_extra_fields_rejected(
        self,
        async_client: AsyncClient,
        c17_api_context: dict[str, Any],
    ) -> None:
        headers = admin_headers(c17_api_context)
        response = await async_client.post(
            "/api/fechas-academicas",
            json={
                "materia_id": str(c17_api_context["materia_id"]),
                "cohorte_id": str(c17_api_context["cohorte_id"]),
                "tipo": "Parcial",
                "numero": 1,
                "periodo": "2026-1C",
                "fecha": "2026-05-15",
                "titulo": "Extra",
                "extra_field": "should be rejected",
            },
            headers=headers,
        )
        assert response.status_code == 422

    async def test_list_fechas_filters(
        self,
        async_client: AsyncClient,
        c17_api_context: dict[str, Any],
    ) -> None:
        headers = admin_headers(c17_api_context)
        response = await async_client.get("/api/fechas-academicas", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_list_calendario_by_date_range(
        self,
        async_client: AsyncClient,
        c17_api_context: dict[str, Any],
    ) -> None:
        headers = admin_headers(c17_api_context)
        response = await async_client.get(
            "/api/fechas-academicas/calendario",
            params={"desde": "2026-01-01", "hasta": "2026-12-31"},
            headers=headers,
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_get_lms_fragment_returns_html(
        self,
        async_client: AsyncClient,
        c17_api_context: dict[str, Any],
    ) -> None:
        headers = admin_headers(c17_api_context)
        await async_client.post(
            "/api/fechas-academicas",
            json={
                "materia_id": str(c17_api_context["materia_id"]),
                "cohorte_id": str(c17_api_context["cohorte_id"]),
                "tipo": "Parcial",
                "numero": 1,
                "periodo": "2026-1C",
                "fecha": "2026-05-15",
                "titulo": "LMS Test",
            },
            headers=headers,
        )
        response = await async_client.get(
            "/api/fechas-academicas/lms-fragment",
            params={
                "materia_id": str(c17_api_context["materia_id"]),
                "cohorte_id": str(c17_api_context["cohorte_id"]),
            },
            headers=headers,
        )
        assert response.status_code == 200
        assert "<table>" in response.json()["contenido"]

    async def test_get_lms_fragment_empty_returns_message(
        self,
        async_client: AsyncClient,
        c17_api_context: dict[str, Any],
    ) -> None:
        headers = admin_headers(c17_api_context)
        response = await async_client.get(
            "/api/fechas-academicas/lms-fragment",
            params={
                "materia_id": str(c17_api_context["materia_id"]),
                "cohorte_id": str(c17_api_context["cohorte_id"]),
            },
            headers=headers,
        )
        assert response.status_code == 200
        assert "No hay fechas académicas programadas" in response.json()["contenido"]

    async def test_get_fecha_returns_200(
        self,
        async_client: AsyncClient,
        c17_api_context: dict[str, Any],
    ) -> None:
        headers = admin_headers(c17_api_context)
        created = await async_client.post(
            "/api/fechas-academicas",
            json={
                "materia_id": str(c17_api_context["materia_id"]),
                "cohorte_id": str(c17_api_context["cohorte_id"]),
                "tipo": "Coloquio",
                "numero": 1,
                "periodo": "2026-1C",
                "fecha": "2026-07-15",
                "titulo": "Coloquio Final",
            },
            headers=headers,
        )
        fecha_id = created.json()["id"]
        response = await async_client.get(f"/api/fechas-academicas/{fecha_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["titulo"] == "Coloquio Final"

    async def test_update_fecha_returns_200(
        self,
        async_client: AsyncClient,
        c17_api_context: dict[str, Any],
    ) -> None:
        headers = admin_headers(c17_api_context)
        created = await async_client.post(
            "/api/fechas-academicas",
            json={
                "materia_id": str(c17_api_context["materia_id"]),
                "cohorte_id": str(c17_api_context["cohorte_id"]),
                "tipo": "Parcial",
                "numero": 1,
                "periodo": "2026-1C",
                "fecha": "2026-05-15",
                "titulo": "Before",
            },
            headers=headers,
        )
        fecha_id = created.json()["id"]
        response = await async_client.put(
            f"/api/fechas-academicas/{fecha_id}",
            json={"titulo": "After", "fecha": "2026-05-20"},
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json()["titulo"] == "After"

    async def test_delete_fecha_returns_204(
        self,
        async_client: AsyncClient,
        c17_api_context: dict[str, Any],
    ) -> None:
        headers = admin_headers(c17_api_context)
        created = await async_client.post(
            "/api/fechas-academicas",
            json={
                "materia_id": str(c17_api_context["materia_id"]),
                "cohorte_id": str(c17_api_context["cohorte_id"]),
                "tipo": "Recuperatorio",
                "numero": 1,
                "periodo": "2026-1C",
                "fecha": "2026-08-01",
                "titulo": "Recup",
            },
            headers=headers,
        )
        fecha_id = created.json()["id"]
        response = await async_client.delete(f"/api/fechas-academicas/{fecha_id}", headers=headers)
        assert response.status_code == 204

    async def test_permission_guard_returns_403(
        self,
        async_client: AsyncClient,
        c17_api_context: dict[str, Any],
    ) -> None:
        headers = no_perm_headers(c17_api_context)
        response = await async_client.get("/api/fechas-academicas", headers=headers)
        assert response.status_code == 403
