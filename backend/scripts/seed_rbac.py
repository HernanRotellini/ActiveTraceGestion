"""Seed roles, permissions and role-permission assignments for the seed tenant.

Idempotent — safe to run multiple times. Uses existence checks (no ON CONFLICT
since the tables lack unique constraints in production).

This data SHOULD have been inserted by the migrations:
  - 20260602_0003_rbac_foundation  (roles, 23 permisos, 52 assignments)
  - 20260613_0001_fix_frontend_permissions  (9 permisos, 24 assignments)

But both were `alembic stamp head` without executing DML.

Usage:
    docker exec active-trace-api-1 python scripts/seed_rbac.py
"""

import asyncio
import sys

from app.core.config import Settings
from app.core.database import create_engine_from_url, dispose_engine, get_sessionmaker
from sqlalchemy import text

SEED_TENANT_ID = "00000000-0000-0000-0000-000000000001"

# ── Roles (7) ─────────────────────────────────────────────────────
ROLES = [
    ("ALUMNO", "Alumno"),
    ("TUTOR", "Tutor"),
    ("PROFESOR", "Profesor"),
    ("COORDINADOR", "Coordinador"),
    ("NEXO", "Nexo"),
    ("ADMIN", "Administrador"),
    ("FINANZAS", "Finanzas"),
]

# ── Permisos (32 total) ───────────────────────────────────────────
# 23 originales (from 20260602_0003)
PERMISOS_ORIGINALES = [
    ("academico:ver_estado_propio", "Ver estado académico propio", "academico", "ver_estado_propio"),
    ("evaluaciones:reservar", "Reservar evaluación", "evaluaciones", "reservar"),
    ("avisos:confirmar", "Confirmar avisos", "avisos", "confirmar"),
    ("calificaciones:importar", "Importar calificaciones", "calificaciones", "importar"),
    ("atrasados:ver", "Ver atrasados", "atrasados", "ver"),
    ("entregas:detectar_sin_corregir", "Detectar entregas sin corregir", "entregas", "detectar_sin_corregir"),
    ("comunicacion:enviar", "Enviar comunicación", "comunicacion", "enviar"),
    ("comunicacion:aprobar", "Aprobar comunicación", "comunicacion", "aprobar"),
    ("encuentros:gestionar", "Gestionar encuentros", "encuentros", "gestionar"),
    ("guardias:registrar", "Registrar guardias", "guardias", "registrar"),
    ("tareas:gestionar", "Gestionar tareas", "tareas", "gestionar"),
    ("avisos:publicar", "Publicar avisos", "avisos", "publicar"),
    ("equipos:asignar", "Asignar equipos", "equipos", "asignar"),
    ("estructura:gestionar", "Gestionar estructura académica", "estructura", "gestionar"),
    ("usuarios:gestionar", "Gestionar usuarios", "usuarios", "gestionar"),
    ("auditoria:ver", "Ver auditoría", "auditoria", "ver"),
    ("liquidaciones:operar_grilla", "Operar grilla de liquidaciones", "liquidaciones", "operar_grilla"),
    ("liquidaciones:calcular_cerrar", "Calcular y cerrar liquidaciones", "liquidaciones", "calcular_cerrar"),
    ("facturas:gestionar", "Gestionar facturas", "facturas", "gestionar"),
    ("tenant:configurar", "Configurar tenant", "tenant", "configurar"),
    ("impersonacion:usar", "Usar impersonación", "impersonacion", "usar"),
    ("coloquios:gestionar", "Gestionar coloquios", "coloquios", "gestionar"),
    ("coloquios:reservar", "Reservar coloquio", "coloquios", "reservar"),
]

# 9 nuevos (from 20260613_0001)
PERMISOS_NUEVOS = [
    ("calificaciones:ver", "Ver calificaciones", "calificaciones", "ver"),
    ("equipos:ver", "Ver equipos docentes", "equipos", "ver"),
    ("equipos:gestionar", "Gestionar equipos docentes", "equipos", "gestionar"),
    ("avisos:ver", "Ver avisos", "avisos", "ver"),
    ("avisos:gestionar", "Gestionar avisos", "avisos", "gestionar"),
    ("tareas:ver", "Ver tareas internas", "tareas", "ver"),
    ("encuentros:ver", "Ver encuentros", "encuentros", "ver"),
    ("coloquios:ver", "Ver coloquios", "coloquios", "ver"),
    ("liquidaciones:ver", "Ver liquidaciones y facturas", "liquidaciones", "ver"),
]

ALL_PERMISOS = PERMISOS_ORIGINALES + PERMISOS_NUEVOS

# ── Role-Permission Assignments (76 total) ────────────────────────
# 52 originales (from 20260602_0003)
MATRIX_ORIGINAL = [
    ("ALUMNO", "academico:ver_estado_propio", "global"),
    ("ALUMNO", "evaluaciones:reservar", "global"),
    ("ALUMNO", "coloquios:reservar", "global"),
    ("TUTOR", "avisos:confirmar", "global"),
    ("TUTOR", "atrasados:ver", "propio"),
    ("TUTOR", "entregas:detectar_sin_corregir", "global"),
    ("TUTOR", "encuentros:gestionar", "global"),
    ("TUTOR", "guardias:registrar", "propio"),
    ("PROFESOR", "avisos:confirmar", "global"),
    ("PROFESOR", "calificaciones:importar", "propio"),
    ("PROFESOR", "atrasados:ver", "propio"),
    ("PROFESOR", "entregas:detectar_sin_corregir", "propio"),
    ("PROFESOR", "comunicacion:enviar", "propio"),
    ("PROFESOR", "encuentros:gestionar", "propio"),
    ("PROFESOR", "guardias:registrar", "propio"),
    ("PROFESOR", "tareas:gestionar", "propio"),
    ("COORDINADOR", "avisos:confirmar", "global"),
    ("COORDINADOR", "calificaciones:importar", "global"),
    ("COORDINADOR", "atrasados:ver", "global"),
    ("COORDINADOR", "entregas:detectar_sin_corregir", "global"),
    ("COORDINADOR", "comunicacion:enviar", "global"),
    ("COORDINADOR", "comunicacion:aprobar", "global"),
    ("COORDINADOR", "encuentros:gestionar", "global"),
    ("COORDINADOR", "guardias:registrar", "global"),
    ("COORDINADOR", "tareas:gestionar", "global"),
    ("COORDINADOR", "avisos:publicar", "global"),
    ("COORDINADOR", "equipos:asignar", "global"),
    ("COORDINADOR", "auditoria:ver", "propio"),
    ("COORDINADOR", "coloquios:gestionar", "global"),
    ("NEXO", "avisos:confirmar", "global"),
    ("ADMIN", "avisos:confirmar", "global"),
    ("ADMIN", "calificaciones:importar", "global"),
    ("ADMIN", "atrasados:ver", "global"),
    ("ADMIN", "entregas:detectar_sin_corregir", "global"),
    ("ADMIN", "comunicacion:enviar", "global"),
    ("ADMIN", "comunicacion:aprobar", "global"),
    ("ADMIN", "encuentros:gestionar", "global"),
    ("ADMIN", "guardias:registrar", "global"),
    ("ADMIN", "tareas:gestionar", "global"),
    ("ADMIN", "avisos:publicar", "global"),
    ("ADMIN", "equipos:asignar", "global"),
    ("ADMIN", "estructura:gestionar", "global"),
    ("ADMIN", "usuarios:gestionar", "global"),
    ("ADMIN", "auditoria:ver", "global"),
    ("ADMIN", "tenant:configurar", "global"),
    ("ADMIN", "impersonacion:usar", "global"),
    ("ADMIN", "coloquios:gestionar", "global"),
    ("ADMIN", "coloquios:reservar", "global"),
    ("FINANZAS", "avisos:confirmar", "global"),
    ("FINANZAS", "auditoria:ver", "global"),
    ("FINANZAS", "liquidaciones:operar_grilla", "global"),
    ("FINANZAS", "liquidaciones:calcular_cerrar", "global"),
    ("FINANZAS", "facturas:gestionar", "global"),
]

# 24 nuevas asignaciones (from 20260613_0001)
MATRIX_NUEVAS = [
    ("PROFESOR", "calificaciones:ver", "propio"),
    ("PROFESOR", "equipos:ver", "propio"),
    ("PROFESOR", "avisos:ver", "propio"),
    ("PROFESOR", "tareas:ver", "propio"),
    ("PROFESOR", "encuentros:ver", "propio"),
    ("PROFESOR", "coloquios:ver", "propio"),
    ("TUTOR", "calificaciones:ver", "propio"),
    ("TUTOR", "encuentros:ver", "propio"),
    ("TUTOR", "tareas:ver", "propio"),
    ("TUTOR", "avisos:ver", "propio"),
    ("COORDINADOR", "calificaciones:ver", "global"),
    ("COORDINADOR", "equipos:ver", "global"),
    ("COORDINADOR", "equipos:gestionar", "global"),
    ("COORDINADOR", "avisos:ver", "global"),
    ("COORDINADOR", "avisos:gestionar", "global"),
    ("COORDINADOR", "tareas:ver", "global"),
    ("COORDINADOR", "encuentros:ver", "global"),
    ("COORDINADOR", "coloquios:ver", "global"),
    ("COORDINADOR", "liquidaciones:ver", "global"),
    ("ADMIN", "calificaciones:ver", "global"),
    ("ADMIN", "equipos:ver", "global"),
    ("ADMIN", "equipos:gestionar", "global"),
    ("ADMIN", "avisos:ver", "global"),
    ("ADMIN", "avisos:gestionar", "global"),
    ("ADMIN", "tareas:ver", "global"),
    ("ADMIN", "encuentros:ver", "global"),
    ("ADMIN", "coloquios:ver", "global"),
    ("ADMIN", "liquidaciones:ver", "global"),
    ("ADMIN", "liquidaciones:operar_grilla", "global"),
    ("ADMIN", "liquidaciones:calcular_cerrar", "global"),
    ("ADMIN", "facturas:gestionar", "global"),
    ("FINANZAS", "liquidaciones:ver", "global"),
]

ALL_MATRIX = MATRIX_ORIGINAL + MATRIX_NUEVAS


async def _exists(session, table: str, column: str, value: str, tenant_id: str) -> bool:
    """Check if a record exists for this tenant."""
    result = await session.execute(
        text(f"SELECT 1 FROM {table} WHERE {column} = :value AND tenant_id = :tenant_id LIMIT 1"),
        {"value": value, "tenant_id": tenant_id},
    )
    return result.fetchone() is not None


async def main() -> None:
    settings = Settings()
    connect_args: dict[str, object] = {}
    if sys.platform == "win32":
        connect_args["ssl"] = False
    create_engine_from_url(settings.DATABASE_URL, connect_args=connect_args)
    sessionmaker = get_sessionmaker()

    async with sessionmaker() as session:
        # ── 1. Insert roles ──────────────────────────────────────
        print("── Insertando roles ──")
        for codigo, nombre in ROLES:
            if await _exists(session, "roles", "codigo", codigo, SEED_TENANT_ID):
                print(f"  ─ ya existe: {codigo}")
                continue
            await session.execute(
                text("""
                    INSERT INTO roles (id, tenant_id, codigo, nombre, created_at, updated_at)
                    VALUES (gen_random_uuid(), :tenant_id, :codigo, :nombre, now(), now())
                """),
                {"tenant_id": SEED_TENANT_ID, "codigo": codigo, "nombre": nombre},
            )
            print(f"  ✓ creado: {codigo}")

        # ── 2. Insert permisos ────────────────────────────────────
        print("\n── Insertando permisos ──")
        for codigo, nombre, modulo, accion in ALL_PERMISOS:
            if await _exists(session, "permisos", "codigo", codigo, SEED_TENANT_ID):
                print(f"  ─ ya existe: {codigo}")
                continue
            await session.execute(
                text("""
                    INSERT INTO permisos (id, tenant_id, codigo, nombre, modulo, accion, created_at, updated_at)
                    VALUES (gen_random_uuid(), :tenant_id, :codigo, :nombre, :modulo, :accion, now(), now())
                """),
                {
                    "tenant_id": SEED_TENANT_ID,
                    "codigo": codigo,
                    "nombre": nombre,
                    "modulo": modulo,
                    "accion": accion,
                },
            )
            print(f"  ✓ creado: {codigo}")

        # ── 3. Insert role-permission assignments ─────────────────
        print("\n── Insertando asignaciones rol→permiso ──")
        count_created = 0
        count_skipped = 0
        for rol_codigo, permiso_codigo, alcance in ALL_MATRIX:
            # Check if this assignment already exists
            exists_check = await session.execute(
                text("""
                    SELECT 1 FROM roles_permisos rp
                    JOIN roles r ON rp.rol_id = r.id
                    JOIN permisos p ON rp.permiso_id = p.id
                    WHERE r.codigo = :rol_codigo
                      AND p.codigo = :permiso_codigo
                      AND rp.tenant_id = :tenant_id
                    LIMIT 1
                """),
                {"rol_codigo": rol_codigo, "permiso_codigo": permiso_codigo, "tenant_id": SEED_TENANT_ID},
            )
            if exists_check.fetchone():
                count_skipped += 1
                continue

            # Insert using a subquery to lookup rol_id and permiso_id
            await session.execute(
                text("""
                    INSERT INTO roles_permisos (id, tenant_id, rol_id, permiso_id, habilitado, alcance, created_at, updated_at)
                    SELECT
                        gen_random_uuid(),
                        :tenant_id,
                        r.id,
                        p.id,
                        true,
                        :alcance,
                        now(),
                        now()
                    FROM roles r, permisos p
                    WHERE r.codigo = :rol_codigo
                      AND p.codigo = :permiso_codigo
                      AND r.tenant_id = :tenant_id
                      AND p.tenant_id = :tenant_id
                """),
                {
                    "tenant_id": SEED_TENANT_ID,
                    "rol_codigo": rol_codigo,
                    "permiso_codigo": permiso_codigo,
                    "alcance": alcance,
                },
            )
            count_created += 1

        print(f"  ✓ creadas: {count_created}")
        print(f"  ─ ya existían: {count_skipped}")

        # ── 4. Commit ─────────────────────────────────────────────
        await session.commit()
        print(f"\n✅ Seed RBAC completado exitosamente.")
        print(f"    Roles: {len(ROLES)}")
        print(f"    Permisos: {len(ALL_PERMISOS)}")
        print(f"    Asignaciones: {count_created} creadas + {count_skipped} existentes")

    await dispose_engine()


if __name__ == "__main__":
    asyncio.run(main())
