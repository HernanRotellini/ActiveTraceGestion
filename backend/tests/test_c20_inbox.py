"""Tests para C-20 mensajería interna (inbox).

Strict TDD: RED → GREEN → TRIANGULATE → REFACTOR.
"""

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


@pytest.fixture
async def inbox_schema(db_engine: None):
    from app.core.database import get_sessionmaker
    from app.models.usuarios_asignaciones import Usuario  # noqa: F401
    from app.models.hilo_mensaje import HiloMensaje  # noqa: F401
    from app.models.mensaje_interno import MensajeInterno  # noqa: F401
    from app.services.auth import login_rate_limiter

    login_rate_limiter.reset_all()

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        connection = await session.connection()
        await connection.execute(
            text(
                "DROP TABLE IF EXISTS mensajes_internos, hilos_mensajes, "
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
async def seed_inbox(db_session: AsyncSession) -> dict[str, Any]:
    tenant = Tenant(name="Tenant test", code="test")
    db_session.add(tenant)
    await db_session.flush()

    user1 = AuthUser(
        tenant_id=tenant.id,
        email="user1@test.com",
        password_hash=hash_password("password"),
        roles=["ALUMNO"],
        is_active=True,
    )
    db_session.add(user1)
    await db_session.flush()

    user2 = AuthUser(
        tenant_id=tenant.id,
        email="user2@test.com",
        password_hash=hash_password("password"),
        roles={"ALUMNO"},
        is_active=True,
    )
    db_session.add(user2)
    await db_session.flush()

    user3 = AuthUser(
        tenant_id=tenant.id,
        email="user3@test.com",
        password_hash=hash_password("password"),
        roles=["ALUMNO"],
        is_active=True,
    )
    db_session.add(user3)
    await db_session.flush()

    from app.models.usuarios_asignaciones import Usuario

    u1 = Usuario(tenant_id=tenant.id, nombre="User1", apellidos="Test", email="user1@test.com")
    u2 = Usuario(tenant_id=tenant.id, nombre="User2", apellidos="Test", email="user2@test.com")
    u3 = Usuario(tenant_id=tenant.id, nombre="User3", apellidos="Test", email="user3@test.com")
    db_session.add_all([u1, u2, u3])
    await db_session.flush()
    await db_session.commit()

    return {
        "tenant_id": tenant.id,
        "tenant_code": tenant.code,
        "user1_id": user1.id,
        "user2_id": user2.id,
        "user3_id": user3.id,
        "u1_id": u1.id,
        "u2_id": u2.id,
        "u3_id": u3.id,
    }


async def login(client: AsyncClient, tenant_code: str = "test", email: str = "user1@test.com") -> dict[str, Any]:
    resp = await client.post(
        "/api/auth/login",
        json={"tenant_code": tenant_code, "email": email, "password": "password"},
    )
    return resp.json()


async def auth_headers(client: AsyncClient, email: str = "user1@test.com") -> dict[str, str]:
    resp = await client.post(
        "/api/auth/login",
        json={"tenant_code": "test", "email": email, "password": "password"},
    )
    data = resp.json()
    assert "access_token" in data, f"Login failed for {email}: {data}"
    return {"Authorization": f"Bearer {data['access_token']}"}


@pytest.mark.usefixtures("inbox_schema", "seed_inbox")
class TestInboxList:
    async def test_empty_inbox_returns_empty_list(self, async_client: AsyncClient):
        headers = await auth_headers(async_client, email="user1@test.com")
        resp = await async_client.get("/api/v1/inbox", headers=headers)
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_list_returns_threads_for_participant(self, async_client: AsyncClient, seed_inbox: dict[str, Any]):
        headers1 = await auth_headers(async_client, email="user1@test.com")
        create_resp = await async_client.post(
            "/api/v1/inbox",
            headers=headers1,
            json={
                "asunto": "Test asunto",
                "destinatarios": [str(seed_inbox["u2_id"])],
                "cuerpo": "Hola mundo",
            },
        )
        assert create_resp.status_code == 201

        resp = await async_client.get("/api/v1/inbox", headers=headers1)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["asunto"] == "Test asunto"
        assert data[0]["ultimo_mensaje"] == "Hola mundo"

    async def test_other_user_does_not_see_thread(self, async_client: AsyncClient, seed_inbox: dict[str, Any]):
        headers1 = await auth_headers(async_client, email="user1@test.com")
        await async_client.post(
            "/api/v1/inbox",
            headers=headers1,
            json={
                "asunto": "Privado",
                "destinatarios": [str(seed_inbox["u2_id"])],
                "cuerpo": "Solo entre nosotros",
            },
        )
        headers3 = await auth_headers(async_client, email="user3@test.com")
        resp = await async_client.get("/api/v1/inbox", headers=headers3)
        assert resp.status_code == 200
        assert resp.json() == []


@pytest.mark.usefixtures("inbox_schema", "seed_inbox")
class TestCreateThread:
    async def test_create_new_thread(self, async_client: AsyncClient, seed_inbox: dict[str, Any]):
        headers = await auth_headers(async_client, email="user1@test.com")
        resp = await async_client.post(
            "/api/v1/inbox",
            headers=headers,
            json={
                "asunto": "Consulta sobre materia",
                "destinatarios": [str(seed_inbox["u2_id"])],
                "cuerpo": "Hola, necesito información",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["asunto"] == "Consulta sobre materia"
        assert str(seed_inbox["u1_id"]) in data["participantes_ids"]
        assert str(seed_inbox["u2_id"]) in data["participantes_ids"]

    async def test_thread_with_non_existent_user_returns_404(self, async_client: AsyncClient):
        headers = await auth_headers(async_client, email="user1@test.com")
        fake_id = "00000000-0000-0000-0000-000000000000"
        resp = await async_client.post(
            "/api/v1/inbox",
            headers=headers,
            json={
                "asunto": "Test",
                "destinatarios": [fake_id],
                "cuerpo": "Mensaje",
            },
        )
        assert resp.status_code == 404


@pytest.mark.usefixtures("inbox_schema", "seed_inbox")
class TestViewThread:
    async def test_view_thread_messages(self, async_client: AsyncClient, seed_inbox: dict[str, Any]):
        headers1 = await auth_headers(async_client, email="user1@test.com")
        create_resp = await async_client.post(
            "/api/v1/inbox",
            headers=headers1,
            json={
                "asunto": "Mi hilo",
                "destinatarios": [str(seed_inbox["u2_id"])],
                "cuerpo": "Primer mensaje",
            },
        )
        hilo_id = create_resp.json()["id"]

        resp = await async_client.get(f"/api/v1/inbox/{hilo_id}", headers=headers1)
        assert resp.status_code == 200
        data = resp.json()
        assert data["asunto"] == "Mi hilo"
        assert len(data["mensajes"]) == 1
        assert data["mensajes"][0]["cuerpo"] == "Primer mensaje"

    async def test_non_participant_gets_404(self, async_client: AsyncClient, seed_inbox: dict[str, Any]):
        headers1 = await auth_headers(async_client, email="user1@test.com")
        create_resp = await async_client.post(
            "/api/v1/inbox",
            headers=headers1,
            json={
                "asunto": "Privado",
                "destinatarios": [str(seed_inbox["u2_id"])],
                "cuerpo": "Secreto",
            },
        )
        hilo_id = create_resp.json()["id"]

        headers3 = await auth_headers(async_client, email="user3@test.com")
        resp = await async_client.get(f"/api/v1/inbox/{hilo_id}", headers=headers3)
        assert resp.status_code == 404


@pytest.mark.usefixtures("inbox_schema", "seed_inbox")
class TestReply:
    async def test_reply_to_thread(self, async_client: AsyncClient, seed_inbox: dict[str, Any]):
        headers1 = await auth_headers(async_client, email="user1@test.com")
        create_resp = await async_client.post(
            "/api/v1/inbox",
            headers=headers1,
            json={
                "asunto": "Conversación",
                "destinatarios": [str(seed_inbox["u2_id"])],
                "cuerpo": "Hola",
            },
        )
        hilo_id = create_resp.json()["id"]

        resp = await async_client.post(
            f"/api/v1/inbox/{hilo_id}/responder",
            headers=headers1,
            json={"cuerpo": "Gracias por la información"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["cuerpo"] == "Gracias por la información"
        assert data["hilo_id"] == hilo_id
        assert data["remitente_id"] is not None

    async def test_non_participant_cannot_reply(self, async_client: AsyncClient, seed_inbox: dict[str, Any]):
        headers1 = await auth_headers(async_client, email="user1@test.com")
        create_resp = await async_client.post(
            "/api/v1/inbox",
            headers=headers1,
            json={
                "asunto": "Privado",
                "destinatarios": [str(seed_inbox["u2_id"])],
                "cuerpo": "Hola",
            },
        )
        hilo_id = create_resp.json()["id"]

        headers3 = await auth_headers(async_client, email="user3@test.com")
        resp = await async_client.post(
            f"/api/v1/inbox/{hilo_id}/responder",
            headers=headers3,
            json={"cuerpo": "Intruso"},
        )
        assert resp.status_code == 404
