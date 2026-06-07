"""Tests de API para C-16 Tareas internas."""

from typing import Any
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from tests.test_tareas_internas import crear_materia, crear_usuario, tareas_schema  # noqa: F401


@pytest.fixture
async def tareas_api_context(db_session: AsyncSession, tareas_schema: None) -> dict[str, Any]:
    from app.models.auth import AuthUser
    from app.models.rbac import Permiso, Rol, RolPermiso
    from app.models.tenant import Tenant

    tenant = Tenant(name="Tenant tareas API", code="tareas-api")
    other_tenant = Tenant(name="Otro tenant tareas API", code="tareas-api-otro")
    db_session.add_all([tenant, other_tenant])
    await db_session.flush()

    admin = AuthUser(
        tenant_id=tenant.id,
        email="admin-tareas@example.com",
        password_hash=hash_password("password"),
        roles=["ADMIN"],
        is_active=True,
    )
    no_permission = AuthUser(
        tenant_id=tenant.id,
        email="sin-permiso-tareas@example.com",
        password_hash=hash_password("password"),
        roles=["LECTOR"],
        is_active=True,
    )
    db_session.add_all([admin, no_permission])
    await db_session.flush()

    rol = Rol(tenant_id=tenant.id, codigo="ADMIN", nombre="Admin")
    permiso = Permiso(
        tenant_id=tenant.id,
        codigo="tareas:gestionar",
        nombre="Gestionar tareas internas",
        modulo="tareas",
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

    actor_id = await crear_usuario(db_session, tenant.id, id=admin.id, email="actor-api@example.com")
    asignado_id = await crear_usuario(db_session, tenant.id, email="asignado-api@example.com")
    delegado_id = await crear_usuario(db_session, tenant.id, email="delegado-api@example.com")
    materia_id = await crear_materia(db_session, tenant.id)
    cross_user_id = await crear_usuario(db_session, other_tenant.id, email="cross-api@example.com")
    await db_session.commit()

    return {
        "tenant_code": tenant.code,
        "admin_id": admin.id,
        "no_permission_email": no_permission.email,
        "actor_id": actor_id,
        "asignado_id": asignado_id,
        "delegado_id": delegado_id,
        "materia_id": materia_id,
        "cross_user_id": cross_user_id,
    }


async def tareas_headers(
    client: AsyncClient,
    context: dict[str, Any],
    email: str = "admin-tareas@example.com",
) -> dict[str, str]:
    response = await client.post(
        "/api/auth/login",
        json={"tenant_code": context["tenant_code"], "email": email, "password": "password"},
    )
    data = response.json()
    assert "access_token" in data, data
    return {"Authorization": f"Bearer {data['access_token']}"}


class TestTareasAPI:
    async def test_create_task_uses_jwt_identity_and_rejects_client_controlled_identity(
        self,
        async_client: AsyncClient,
        tareas_api_context: dict[str, Any],
    ) -> None:
        headers = await tareas_headers(async_client, tareas_api_context)

        response = await async_client.post(
            "/api/tareas",
            json={
                "titulo": "Coordinar tutor",
                "descripcion": "Revisar entregas atrasadas",
                "asignado_a": str(tareas_api_context["asignado_id"]),
                "materia_id": str(tareas_api_context["materia_id"]),
                "tenant_id": str(uuid4()),
                "asignado_por": str(uuid4()),
            },
            headers=headers,
        )

        assert response.status_code == 422

        valid = await async_client.post(
            "/api/tareas",
            json={
                "titulo": "Coordinar tutor",
                "descripcion": "Revisar entregas atrasadas",
                "asignado_a": str(tareas_api_context["asignado_id"]),
                "materia_id": str(tareas_api_context["materia_id"]),
            },
            headers=headers,
        )

        assert valid.status_code == 201
        data = valid.json()
        assert data["asignado_por"] == str(tareas_api_context["admin_id"])
        assert data["asignado_a"] == str(tareas_api_context["asignado_id"])
        assert data["estado"] == "Pendiente"
        assert "tenant_id" not in data

    async def test_my_tasks_and_global_filters_are_tenant_scoped(
        self,
        async_client: AsyncClient,
        tareas_api_context: dict[str, Any],
    ) -> None:
        headers = await tareas_headers(async_client, tareas_api_context)
        created = await async_client.post(
            "/api/tareas",
            json={
                "titulo": "Buscar Moodle",
                "descripcion": "Resolver tarea filtrable",
                "asignado_a": str(tareas_api_context["asignado_id"]),
                "materia_id": str(tareas_api_context["materia_id"]),
            },
            headers=headers,
        )
        tarea_id = created.json()["id"]

        mine = await async_client.get("/api/tareas/mis", headers=headers)
        assert mine.status_code == 200
        assert mine.json() == []

        global_response = await async_client.get(
            f"/api/tareas?asignado_a={tareas_api_context['asignado_id']}&materia_id={tareas_api_context['materia_id']}&estado=Pendiente&search=moodle",
            headers=headers,
        )

        assert global_response.status_code == 200
        assert [item["id"] for item in global_response.json()] == [tarea_id]

    async def test_detail_delegate_status_and_comments_flow(
        self,
        async_client: AsyncClient,
        tareas_api_context: dict[str, Any],
    ) -> None:
        headers = await tareas_headers(async_client, tareas_api_context)
        created = await async_client.post(
            "/api/tareas",
            json={
                "titulo": "Hilo completo",
                "descripcion": "Probar detalle",
                "asignado_a": str(tareas_api_context["asignado_id"]),
            },
            headers=headers,
        )
        tarea_id = created.json()["id"]

        delegated = await async_client.post(
            f"/api/tareas/{tarea_id}/delegar",
            json={"asignado_a": str(tareas_api_context["delegado_id"])},
            headers=headers,
        )
        assert delegated.status_code == 200
        assert delegated.json()["asignado_a"] == str(tareas_api_context["delegado_id"])

        in_progress = await async_client.patch(
            f"/api/tareas/{tarea_id}/estado",
            json={"estado": "En progreso"},
            headers=headers,
        )
        assert in_progress.status_code == 200
        assert in_progress.json()["estado"] == "En progreso"

        comment = await async_client.post(
            f"/api/tareas/{tarea_id}/comentarios",
            json={"texto": "Tomado por coordinación"},
            headers=headers,
        )
        assert comment.status_code == 201
        assert comment.json()["autor_id"] == str(tareas_api_context["admin_id"])

        detail = await async_client.get(f"/api/tareas/{tarea_id}", headers=headers)
        assert detail.status_code == 200
        assert [item["texto"] for item in detail.json()["comentarios"]] == ["Tomado por coordinación"]

    async def test_permission_guard_cross_tenant_and_invalid_payloads(
        self,
        async_client: AsyncClient,
        tareas_api_context: dict[str, Any],
    ) -> None:
        no_permission_headers = await tareas_headers(
            async_client,
            tareas_api_context,
            email=tareas_api_context["no_permission_email"],
        )
        forbidden = await async_client.get("/api/tareas", headers=no_permission_headers)
        assert forbidden.status_code == 403

        headers = await tareas_headers(async_client, tareas_api_context)
        cross_tenant = await async_client.post(
            "/api/tareas",
            json={
                "titulo": "Cross tenant",
                "descripcion": "No debe persistir",
                "asignado_a": str(tareas_api_context["cross_user_id"]),
            },
            headers=headers,
        )
        assert cross_tenant.status_code == 400

        invalid_status = await async_client.patch(
            f"/api/tareas/{uuid4()}/estado",
            json={"estado": "Reabierta"},
            headers=headers,
        )
        assert invalid_status.status_code == 422
