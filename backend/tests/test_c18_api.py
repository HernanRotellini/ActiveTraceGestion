"""Tests de API para C-18 Liquidaciones y Honorarios."""

from datetime import date
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base
from app.core.security import create_access_token, hash_password
from app.models.permisos import (
    FACTURAS_GESTIONAR,
    LIQUIDACIONES_CALCULAR_CERRAR,
    LIQUIDACIONES_OPERAR_GRILLA,
)


@pytest.fixture
async def c18_api_schema(db_engine: None) -> None:
    from app.models.audit_log import AuditLog  # noqa: F401
    from app.models.auth import AuthUser  # noqa: F401
    from app.models.estructura_academica import Carrera, Cohorte, Materia  # noqa: F401
    from app.models.liquidaciones import Factura, Liquidacion, MateriaPlus, SalarioBase, SalarioPlus  # noqa: F401
    from app.models.rbac import Permiso, Rol, RolPermiso  # noqa: F401
    from app.models.tenant import Tenant  # noqa: F401
    from app.models.usuarios_asignaciones import Asignacion, Usuario  # noqa: F401

    from app.core.database import get_sessionmaker

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        connection = await session.connection()
        await connection.execute(text("DROP SCHEMA public CASCADE"))
        await connection.execute(text("CREATE SCHEMA public"))
        await connection.run_sync(Base.metadata.create_all)
        await session.commit()


async def _crear_carrera(db_session: AsyncSession, tenant_id: UUID, codigo: str) -> UUID:
    from app.models.estructura_academica import Carrera

    carrera = Carrera(tenant_id=tenant_id, codigo=codigo, nombre=f"Carrera {codigo}")
    db_session.add(carrera)
    await db_session.flush()
    return carrera.id


async def _crear_cohorte(db_session: AsyncSession, tenant_id: UUID, carrera_id: UUID, nombre: str) -> UUID:
    from app.models.estructura_academica import Cohorte

    cohorte = Cohorte(tenant_id=tenant_id, carrera_id=carrera_id, nombre=nombre, anio=2026, vig_desde=date(2026, 1, 1))
    db_session.add(cohorte)
    await db_session.flush()
    return cohorte.id


async def _crear_materia(db_session: AsyncSession, tenant_id: UUID, codigo: str) -> UUID:
    from app.models.estructura_academica import Materia

    materia = Materia(tenant_id=tenant_id, codigo=codigo, nombre=f"Materia {codigo}")
    db_session.add(materia)
    await db_session.flush()
    return materia.id


async def _crear_usuario(db_session: AsyncSession, tenant_id: UUID, **overrides: Any) -> UUID:
    from app.models.usuarios_asignaciones import Usuario

    defaults = {
        "tenant_id": tenant_id,
        "nombre": "Docente",
        "apellidos": "API",
        "email": f"docente-{uuid4().hex[:8]}@example.com",
        "banco": "Banco Test",
        "cbu": "encrypted-cbu",
        "facturador": False,
    }
    defaults.update(overrides)
    usuario = Usuario(**defaults)
    db_session.add(usuario)
    await db_session.flush()
    return usuario.id


async def _crear_asignacion(
    db_session: AsyncSession,
    tenant_id: UUID,
    *,
    usuario_id: UUID,
    cohorte_id: UUID,
    materia_id: UUID,
    rol: str = "PROFESOR",
) -> None:
    from app.models.usuarios_asignaciones import Asignacion

    db_session.add(
        Asignacion(
            tenant_id=tenant_id,
            usuario_id=usuario_id,
            cohorte_id=cohorte_id,
            materia_id=materia_id,
            rol=rol,
            comisiones=["A", "B"],
            desde=date(2026, 1, 1),
        )
    )
    await db_session.flush()


@pytest.fixture
async def c18_api_context(db_session: AsyncSession, c18_api_schema: None) -> dict[str, Any]:
    from app.core.config import Settings
    from app.models.auth import AuthUser
    from app.models.rbac import Permiso, Rol, RolPermiso
    from app.models.tenant import Tenant

    tenant = Tenant(name="Tenant C18 API", code=f"c18-api-{uuid4().hex[:6]}")
    other_tenant = Tenant(name="Otro Tenant C18 API", code=f"c18-api-other-{uuid4().hex[:6]}")
    db_session.add_all([tenant, other_tenant])
    await db_session.flush()

    admin = AuthUser(
        tenant_id=tenant.id,
        email="finanzas-c18@example.com",
        password_hash=hash_password("password"),
        roles=["FINANZAS"],
        is_active=True,
    )
    no_permission = AuthUser(
        tenant_id=tenant.id,
        email="lector-c18@example.com",
        password_hash=hash_password("password"),
        roles=["LECTOR"],
        is_active=True,
    )
    db_session.add_all([admin, no_permission])
    await db_session.flush()

    rol = Rol(tenant_id=tenant.id, codigo="FINANZAS", nombre="Finanzas")
    db_session.add(rol)
    await db_session.flush()
    for codigo, modulo, accion in [
        (LIQUIDACIONES_OPERAR_GRILLA, "liquidaciones", "operar_grilla"),
        (LIQUIDACIONES_CALCULAR_CERRAR, "liquidaciones", "calcular_cerrar"),
        (FACTURAS_GESTIONAR, "facturas", "gestionar"),
    ]:
        permiso = Permiso(tenant_id=tenant.id, codigo=codigo, nombre=codigo, modulo=modulo, accion=accion)
        db_session.add(permiso)
        await db_session.flush()
        db_session.add(RolPermiso(tenant_id=tenant.id, rol_id=rol.id, permiso_id=permiso.id, habilitado=True, alcance="global"))

    carrera_id = await _crear_carrera(db_session, tenant.id, "C18-API")
    cohorte_id = await _crear_cohorte(db_session, tenant.id, carrera_id, "Cohorte C18 API")
    materia_id = await _crear_materia(db_session, tenant.id, "MAT-C18")
    docente_id = await _crear_usuario(db_session, tenant.id)
    facturante_id = await _crear_usuario(db_session, tenant.id, facturador=True, email="facturante-c18@example.com")
    no_facturante_id = await _crear_usuario(db_session, tenant.id, facturador=False, email="nofact-c18@example.com")
    await _crear_asignacion(db_session, tenant.id, usuario_id=docente_id, cohorte_id=cohorte_id, materia_id=materia_id)

    other_carrera_id = await _crear_carrera(db_session, other_tenant.id, "C18-OTHER")
    other_cohorte_id = await _crear_cohorte(db_session, other_tenant.id, other_carrera_id, "Cohorte Other")
    other_materia_id = await _crear_materia(db_session, other_tenant.id, "MAT-OTHER")
    other_facturante_id = await _crear_usuario(db_session, other_tenant.id, facturador=True, email="facturante-other@example.com")
    await db_session.commit()

    settings = Settings(_env_file=None)  # type: ignore[call-arg]
    admin_token = create_access_token(user_id=admin.id, tenant_id=tenant.id, roles=admin.roles, settings=settings)
    no_perm_token = create_access_token(user_id=no_permission.id, tenant_id=tenant.id, roles=no_permission.roles, settings=settings)
    return {
        "admin_token": admin_token,
        "no_perm_token": no_perm_token,
        "tenant_id": tenant.id,
        "cohorte_id": cohorte_id,
        "materia_id": materia_id,
        "docente_id": docente_id,
        "facturante_id": facturante_id,
        "no_facturante_id": no_facturante_id,
        "other_cohorte_id": other_cohorte_id,
        "other_materia_id": other_materia_id,
        "other_facturante_id": other_facturante_id,
    }


def admin_headers(context: dict[str, Any]) -> dict[str, str]:
    return {"Authorization": f"Bearer {context['admin_token']}"}


def no_perm_headers(context: dict[str, Any]) -> dict[str, str]:
    return {"Authorization": f"Bearer {context['no_perm_token']}"}


async def seed_grilla(async_client: AsyncClient, context: dict[str, Any]) -> None:
    headers = admin_headers(context)
    await async_client.post(
        "/api/liquidaciones/grilla/bases",
        json={"rol": "PROFESOR", "monto": "100000.00", "desde": "2026-01-01"},
        headers=headers,
    )
    await async_client.post(
        "/api/liquidaciones/grilla/pluses",
        json={"rol": "PROFESOR", "grupo": "PROG", "descripcion": "Programacion", "monto": "10000.00", "desde": "2026-01-01"},
        headers=headers,
    )
    await async_client.post(
        "/api/liquidaciones/grilla/materia-plus",
        json={"materia_id": str(context["materia_id"]), "grupo": "PROG", "desde": "2026-01-01"},
        headers=headers,
    )


class TestGrillaSalarialAPI:
    async def test_salario_base_crud_returns_expected_statuses(self, async_client: AsyncClient, c18_api_context: dict[str, Any]) -> None:
        headers = admin_headers(c18_api_context)
        created = await async_client.post(
            "/api/liquidaciones/grilla/bases",
            json={"rol": "PROFESOR", "monto": "120000.00", "desde": "2026-01-01", "hasta": "2026-06-30"},
            headers=headers,
        )
        assert created.status_code == 201
        base_id = created.json()["id"]
        assert created.json()["monto"] == "120000.00"

        listed = await async_client.get("/api/liquidaciones/grilla/bases", headers=headers)
        assert listed.status_code == 200
        assert [item["id"] for item in listed.json()] == [base_id]

        updated = await async_client.put(
            f"/api/liquidaciones/grilla/bases/{base_id}",
            json={"monto": "125000.00", "hasta": "2026-12-31"},
            headers=headers,
        )
        assert updated.status_code == 200
        assert updated.json()["monto"] == "125000.00"

        deleted = await async_client.delete(f"/api/liquidaciones/grilla/bases/{base_id}", headers=headers)
        assert deleted.status_code == 204

    async def test_plus_mapping_permission_invalid_payload_and_cross_tenant(self, async_client: AsyncClient, c18_api_context: dict[str, Any]) -> None:
        headers = admin_headers(c18_api_context)
        plus = await async_client.post(
            "/api/liquidaciones/grilla/pluses",
            json={"rol": "TUTOR", "grupo": "LAB", "descripcion": "Laboratorio", "monto": "15000.00", "desde": "2026-01-01"},
            headers=headers,
        )
        assert plus.status_code == 201

        no_perm = await async_client.post(
            "/api/liquidaciones/grilla/pluses",
            json={"rol": "TUTOR", "grupo": "NO", "descripcion": "Sin permiso", "monto": "1.00", "desde": "2027-01-01"},
            headers=no_perm_headers(c18_api_context),
        )
        assert no_perm.status_code == 403

        invalid = await async_client.post(
            "/api/liquidaciones/grilla/bases",
            json={"rol": "TUTOR", "monto": "1.00", "desde": "2026-01-01", "tenant_id": str(uuid4())},
            headers=headers,
        )
        assert invalid.status_code == 422

        cross_tenant = await async_client.post(
            "/api/liquidaciones/grilla/materia-plus",
            json={"materia_id": str(c18_api_context["other_materia_id"]), "grupo": "LAB", "desde": "2026-01-01"},
            headers=headers,
        )
        assert cross_tenant.status_code == 404


class TestLiquidacionesAPI:
    async def test_preview_close_list_detail_and_duplicate_close(self, async_client: AsyncClient, c18_api_context: dict[str, Any]) -> None:
        headers = admin_headers(c18_api_context)
        await seed_grilla(async_client, c18_api_context)

        preview = await async_client.post(
            "/api/liquidaciones/preview",
            json={"cohorte_id": str(c18_api_context["cohorte_id"]), "periodo": "2026-06"},
            headers=headers,
        )
        assert preview.status_code == 200
        assert preview.json()["total_pagable"] == "120000.00"
        assert preview.json()["items"][0]["monto_plus"] == "20000.00"

        closed = await async_client.post(
            "/api/liquidaciones/cerrar",
            json={"cohorte_id": str(c18_api_context["cohorte_id"]), "periodo": "2026-06"},
            headers=headers,
        )
        assert closed.status_code == 201
        liquidacion_id = closed.json()[0]["id"]

        listed = await async_client.get("/api/liquidaciones", params={"periodo": "2026-06"}, headers=headers)
        assert listed.status_code == 200
        assert [item["id"] for item in listed.json()] == [liquidacion_id]

        detail = await async_client.get(f"/api/liquidaciones/{liquidacion_id}", headers=headers)
        assert detail.status_code == 200
        assert detail.json()["estado"] == "Cerrada"

        duplicate = await async_client.post(
            "/api/liquidaciones/cerrar",
            json={"cohorte_id": str(c18_api_context["cohorte_id"]), "periodo": "2026-06"},
            headers=headers,
        )
        assert duplicate.status_code == 409

    async def test_list_liquidaciones_filtra_por_segmento_y_rechaza_segmento_invalido(
        self, async_client: AsyncClient, db_session: AsyncSession, c18_api_context: dict[str, Any]
    ) -> None:
        from app.models.liquidaciones import RolLiquidacion
        from app.repositories.liquidacion_repository import LiquidacionRepository

        headers = admin_headers(c18_api_context)
        tenant_id = c18_api_context["tenant_id"]
        repo = LiquidacionRepository(db_session, tenant_id)
        general = await repo.create_snapshot(
            cohorte_id=c18_api_context["cohorte_id"],
            usuario_id=c18_api_context["docente_id"],
            periodo="2026-06",
            rol=RolLiquidacion.PROFESOR,
            monto_base=Decimal("100000.00"),
            monto_plus=Decimal("0.00"),
            monto_total=Decimal("100000.00"),
            comisiones=[],
        )
        nexo = await repo.create_snapshot(
            cohorte_id=c18_api_context["cohorte_id"],
            usuario_id=await _crear_usuario(db_session, tenant_id, email="nexo-c18-api@example.com"),
            periodo="2026-06",
            rol=RolLiquidacion.NEXO,
            monto_base=Decimal("50000.00"),
            monto_plus=Decimal("0.00"),
            monto_total=Decimal("50000.00"),
            comisiones=[],
            es_nexo=True,
        )
        facturante = await repo.create_snapshot(
            cohorte_id=c18_api_context["cohorte_id"],
            usuario_id=c18_api_context["facturante_id"],
            periodo="2026-06",
            rol=RolLiquidacion.PROFESOR,
            monto_base=Decimal("100000.00"),
            monto_plus=Decimal("0.00"),
            monto_total=Decimal("100000.00"),
            comisiones=[],
            excluido_por_factura=True,
        )
        await db_session.commit()

        listed_general = await async_client.get("/api/liquidaciones", params={"segmento": "general"}, headers=headers)
        listed_nexo = await async_client.get("/api/liquidaciones", params={"segmento": "nexo"}, headers=headers)
        listed_facturante = await async_client.get("/api/liquidaciones", params={"segmento": "facturante"}, headers=headers)
        invalid = await async_client.get("/api/liquidaciones", params={"segmento": "otro"}, headers=headers)

        assert listed_general.status_code == 200
        assert [item["id"] for item in listed_general.json()] == [str(general.id)]
        assert listed_nexo.status_code == 200
        assert [item["id"] for item in listed_nexo.json()] == [str(nexo.id)]
        assert listed_facturante.status_code == 200
        assert [item["id"] for item in listed_facturante.json()] == [str(facturante.id)]
        assert invalid.status_code == 422

    async def test_liquidacion_guards_invalid_payload_and_cross_tenant(self, async_client: AsyncClient, c18_api_context: dict[str, Any]) -> None:
        headers = admin_headers(c18_api_context)
        no_perm = await async_client.post(
            "/api/liquidaciones/preview",
            json={"cohorte_id": str(c18_api_context["cohorte_id"]), "periodo": "2026-06"},
            headers=no_perm_headers(c18_api_context),
        )
        assert no_perm.status_code == 403

        invalid = await async_client.post(
            "/api/liquidaciones/preview",
            json={"cohorte_id": str(c18_api_context["cohorte_id"]), "periodo": "2026-06", "tenant_id": str(uuid4())},
            headers=headers,
        )
        assert invalid.status_code == 422

        cross_tenant = await async_client.post(
            "/api/liquidaciones/preview",
            json={"cohorte_id": str(c18_api_context["other_cohorte_id"]), "periodo": "2026-06"},
            headers=headers,
        )
        assert cross_tenant.status_code == 404

        detail_cross_tenant = await async_client.get(f"/api/liquidaciones/{uuid4()}", headers=headers)
        assert detail_cross_tenant.status_code == 404


class TestFacturasAPI:
    async def test_factura_crud_and_mark_abonada(self, async_client: AsyncClient, c18_api_context: dict[str, Any]) -> None:
        headers = admin_headers(c18_api_context)
        created = await async_client.post(
            "/api/facturas",
            json={
                "usuario_id": str(c18_api_context["facturante_id"]),
                "periodo": "2026-06",
                "detalle": "Factura junio",
                "referencia_archivo": "opaque://facturas/1",
                "archivo_size_bytes": 2048,
            },
            headers=headers,
        )
        assert created.status_code == 201
        factura_id = created.json()["id"]
        assert created.json()["estado"] == "Pendiente"

        listed = await async_client.get("/api/facturas", params={"periodo": "2026-06"}, headers=headers)
        assert listed.status_code == 200
        assert [item["id"] for item in listed.json()] == [factura_id]

        detail = await async_client.get(f"/api/facturas/{factura_id}", headers=headers)
        assert detail.status_code == 200
        assert detail.json()["detalle"] == "Factura junio"

        updated = await async_client.put(
            f"/api/facturas/{factura_id}",
            json={"detalle": "Factura junio actualizada", "archivo_size_bytes": 4096},
            headers=headers,
        )
        assert updated.status_code == 200
        assert updated.json()["detalle"] == "Factura junio actualizada"

        abonada = await async_client.post(f"/api/facturas/{factura_id}/abonada", headers=headers)
        assert abonada.status_code == 200
        assert abonada.json()["estado"] == "Abonada"

        invalid_transition = await async_client.post(f"/api/facturas/{factura_id}/abonada", headers=headers)
        assert invalid_transition.status_code == 400

        deleted = await async_client.delete(f"/api/facturas/{factura_id}", headers=headers)
        assert deleted.status_code == 204

    async def test_factura_guards_invalid_payload_and_cross_tenant(self, async_client: AsyncClient, c18_api_context: dict[str, Any]) -> None:
        headers = admin_headers(c18_api_context)
        valid_payload = {
            "usuario_id": str(c18_api_context["facturante_id"]),
            "periodo": "2026-06",
            "detalle": "Factura",
            "referencia_archivo": "opaque://facturas/2",
            "archivo_size_bytes": 100,
        }
        no_perm = await async_client.post("/api/facturas", json=valid_payload, headers=no_perm_headers(c18_api_context))
        assert no_perm.status_code == 403

        invalid = await async_client.post(
            "/api/facturas",
            json={**valid_payload, "tenant_id": str(uuid4())},
            headers=headers,
        )
        assert invalid.status_code == 422

        no_facturante = await async_client.post(
            "/api/facturas",
            json={**valid_payload, "usuario_id": str(c18_api_context["no_facturante_id"])},
            headers=headers,
        )
        assert no_facturante.status_code == 400

        cross_tenant = await async_client.post(
            "/api/facturas",
            json={**valid_payload, "usuario_id": str(c18_api_context["other_facturante_id"])},
            headers=headers,
        )
        assert cross_tenant.status_code == 404

        not_found = await async_client.get(f"/api/facturas/{uuid4()}", headers=headers)
        assert not_found.status_code == 404
