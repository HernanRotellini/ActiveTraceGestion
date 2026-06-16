"""Tests for validating frontend payloads against backend endpoints."""

import pytest
from httpx import AsyncClient
from typing import Any
from uuid import uuid4
from datetime import datetime, UTC

from tests.test_tareas_api import tareas_api_context, tareas_headers  # noqa
from tests.test_tareas_internas import tareas_schema  # noqa
from tests.test_avisos import aviso_schema, tenant_id, usuario_id, crear_aviso  # noqa

@pytest.fixture
async def avisos_auth_headers(
    async_client: AsyncClient,
    db_session: Any,
    tenant_id: Any,
    usuario_id: Any
) -> dict[str, str]:
    from app.models.auth import AuthUser
    from app.models.tenant import Tenant
    from app.core.security import hash_password
    from sqlalchemy import select
    from app.models.rbac import Rol, Permiso, RolPermiso

    tenant = await db_session.get(Tenant, tenant_id)
    if not tenant:
        tenant = Tenant(id=tenant_id, name="Test Tenant", code="TEST-FRONTEND")
        db_session.add(tenant)
        await db_session.flush()

    admin = AuthUser(
        tenant_id=tenant_id,
        email="admin-avisos-front@example.com",
        password_hash=hash_password("password"),
        roles=["ADMIN"],
        is_active=True,
        id=usuario_id
    )
    db_session.add(admin)
    await db_session.flush()

    # Add role and permission
    rol = Rol(tenant_id=tenant_id, codigo="ADMIN", nombre="Admin")
    permisos = [
        Permiso(tenant_id=tenant_id, codigo="avisos:publicar", nombre="Publicar", modulo="avisos", accion="publicar"),
        Permiso(tenant_id=tenant_id, codigo="avisos:gestionar", nombre="Gestionar", modulo="avisos", accion="gestionar"),
        Permiso(tenant_id=tenant_id, codigo="avisos:ver", nombre="Ver", modulo="avisos", accion="ver"),
    ]
    db_session.add(rol)
    db_session.add_all(permisos)
    await db_session.flush()

    for p in permisos:
        db_session.add(RolPermiso(tenant_id=tenant_id, rol_id=rol.id, permiso_id=p.id, habilitado=True, alcance="global"))
    
    await db_session.commit()

    response = await async_client.post(
        "/api/auth/login",
        json={"tenant_code": tenant.code, "email": admin.email, "password": "password"},
    )
    data = response.json()
    assert "access_token" in data
    return {"Authorization": f"Bearer {data['access_token']}"}


class TestFrontendPayloads:
    async def test_frontend_tarea_payload(
        self,
        async_client: AsyncClient,
        tareas_schema: None,
        tareas_api_context: dict[str, Any],
    ) -> None:
        """Prueba que el payload base enviado por TareaFormPage.tsx funcione correctamente."""
        headers = await tareas_headers(async_client, tareas_api_context)

        # Payload exacto generado en TareaFormPage.tsx (sin materia_id, sin prioridad, sin fechaLimite)
        base_payload = {
            "titulo": "Nueva Tarea desde el Frontend",
            "descripcion": "Descripción enviada desde el cliente web.",
            "asignado_a": str(tareas_api_context["asignado_id"]),
        }

        response = await async_client.post(
            "/api/tareas",
            json=base_payload,
            headers=headers,
        )

        assert response.status_code == 201, f"El payload falló: {response.json()}"
        data = response.json()
        assert data["titulo"] == base_payload["titulo"]
        assert data["asignado_a"] == base_payload["asignado_a"]


    async def test_frontend_aviso_payload_global(
        self,
        async_client: AsyncClient,
        aviso_schema: None,
        tenant_id: Any,
        usuario_id: Any,
        avisos_auth_headers: dict[str, str],
    ) -> None:
        """Prueba que el payload base enviado por AvisoFormPage.tsx funcione correctamente."""
        # Payload exacto generado en AvisoFormPage.tsx para alcance 'todos'
        payload = {
            "titulo": "Aviso Global Frontend",
            "cuerpo": "Cuerpo del aviso",
            "alcance": "Global",
            "inicio_en": datetime.now(UTC).isoformat(),
        }

        response = await async_client.post(
            "/api/admin/avisos",
            json=payload,
            headers=avisos_auth_headers,
        )

        assert response.status_code == 201, f"El payload falló: {response.json()}"
        data = response.json()
        assert data["alcance"] == "Global"
        assert data["titulo"] == "Aviso Global Frontend"
        
        # Test the update (PUT)
        aviso_id = data["id"]
        update_payload = {
            "titulo": "Aviso Editado",
            "cuerpo": "Cuerpo editado",
            "alcance": "Global",
            "inicio_en": datetime.now(UTC).isoformat(),
        }
        
        response = await async_client.put(
            f"/api/admin/avisos/{aviso_id}",
            json=update_payload,
            headers=avisos_auth_headers,
        )
        assert response.status_code == 200, f"El payload de actualización falló: {response.json()}"


    async def test_frontend_aviso_payload_por_rol(
        self,
        async_client: AsyncClient,
        aviso_schema: None,
        tenant_id: Any,
        usuario_id: Any,
        avisos_auth_headers: dict[str, str],
    ) -> None:
        """Prueba payload para 'por_rol' en AvisoFormPage.tsx."""
        payload = {
            "titulo": "Aviso Por Rol",
            "cuerpo": "Para profesores",
            "alcance": "PorRol",
            "inicio_en": datetime.now(UTC).isoformat(),
            "rol_destino": "PROFESOR"
        }

        response = await async_client.post(
            "/api/admin/avisos",
            json=payload,
            headers=avisos_auth_headers,
        )

        assert response.status_code == 201, f"El payload falló: {response.json()}"
        data = response.json()
        assert data["alcance"] == "PorRol"
        assert data["rol_destino"] == "PROFESOR"
