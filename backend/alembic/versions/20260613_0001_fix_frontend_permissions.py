"""fix frontend permissions — agregar permisos de lectura separados + ADMIN liquidaciones + periodos:gestionar

Nuevos permisos (10):
  - calificaciones:ver, equipos:ver, equipos:gestionar
  - avisos:ver, avisos:gestionar, tareas:ver
  - encuentros:ver, coloquios:ver, liquidaciones:ver
  - periodos:gestionar

Asignaciones nuevas a roles según design.md D1.
ADMIN ahora tiene liquidaciones:operar_grilla, liquidaciones:calcular_cerrar, facturas:gestionar, periodos:gestionar.
COORDINADOR ahora tiene periodos:gestionar para acceder a Setup cuatrimestre.

Revision ID: 20260613_0001
Revises: 20260608_0015
Create Date: 2026-06-13
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260613_0001"
down_revision: str | None = "20260608_0015"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SEED_TENANT_ID = "00000000-0000-0000-0000-000000000001"


def upgrade() -> None:
    # ── Nuevos permisos (10) ──────────────────────────────────────
    nuevos_permisos = [
        ("calificaciones:ver", "Ver calificaciones", "calificaciones", "ver"),
        ("equipos:ver", "Ver equipos docentes", "equipos", "ver"),
        ("equipos:gestionar", "Gestionar equipos docentes", "equipos", "gestionar"),
        ("avisos:ver", "Ver avisos", "avisos", "ver"),
        ("avisos:gestionar", "Gestionar avisos", "avisos", "gestionar"),
        ("tareas:ver", "Ver tareas internas", "tareas", "ver"),
        ("encuentros:ver", "Ver encuentros", "encuentros", "ver"),
        ("coloquios:ver", "Ver coloquios", "coloquios", "ver"),
        ("liquidaciones:ver", "Ver liquidaciones y facturas", "liquidaciones", "ver"),
        ("periodos:gestionar", "Gestionar períodos académicos", "periodos", "gestionar"),
    ]
    permisos_table = sa.table(
        "permisos",
        sa.column("id", postgresql.UUID),
        sa.column("tenant_id", postgresql.UUID),
        sa.column("codigo", sa.String),
        sa.column("nombre", sa.String),
        sa.column("modulo", sa.String),
        sa.column("accion", sa.String),
        sa.column("created_at", sa.DateTime),
        sa.column("updated_at", sa.DateTime),
    )
    for codigo, nombre, modulo, accion in nuevos_permisos:
        op.execute(
            permisos_table.insert().values(
                id=sa.func.gen_random_uuid(),
                tenant_id=SEED_TENANT_ID,
                codigo=codigo,
                nombre=nombre,
                modulo=modulo,
                accion=accion,
                created_at=sa.func.now(),
                updated_at=sa.func.now(),
            )
        )

    # ── Nuevas asignaciones rol-permiso ──────────────────────────
    # Matriz según design.md D1 y especificaciones de rol por pantalla.
    # Formato: (rol_codigo, permiso_codigo, alcance)
    nuevas_asignaciones = [
        # -- PROFESOR --
        ("PROFESOR", "calificaciones:ver", "propio"),
        ("PROFESOR", "equipos:ver", "propio"),
        ("PROFESOR", "avisos:ver", "propio"),
        ("PROFESOR", "tareas:ver", "propio"),
        ("PROFESOR", "encuentros:ver", "propio"),
        ("PROFESOR", "coloquios:ver", "propio"),
        # -- TUTOR --
        ("TUTOR", "calificaciones:ver", "propio"),
        ("TUTOR", "encuentros:ver", "propio"),
        ("TUTOR", "tareas:ver", "propio"),
        ("TUTOR", "avisos:ver", "propio"),
        # -- COORDINADOR --
        ("COORDINADOR", "calificaciones:ver", "global"),
        ("COORDINADOR", "equipos:ver", "global"),
        ("COORDINADOR", "equipos:gestionar", "global"),
        ("COORDINADOR", "avisos:ver", "global"),
        ("COORDINADOR", "avisos:gestionar", "global"),
        ("COORDINADOR", "tareas:ver", "global"),
        ("COORDINADOR", "encuentros:ver", "global"),
        ("COORDINADOR", "coloquios:ver", "global"),
        ("COORDINADOR", "liquidaciones:ver", "global"),
        ("COORDINADOR", "periodos:gestionar", "global"),
        # -- ADMIN -- (todo excepto alumno)
        ("ADMIN", "calificaciones:ver", "global"),
        ("ADMIN", "equipos:ver", "global"),
        ("ADMIN", "equipos:gestionar", "global"),
        ("ADMIN", "avisos:ver", "global"),
        ("ADMIN", "avisos:gestionar", "global"),
        ("ADMIN", "tareas:ver", "global"),
        ("ADMIN", "encuentros:ver", "global"),
        ("ADMIN", "coloquios:ver", "global"),
        ("ADMIN", "liquidaciones:ver", "global"),
        # -- ADMIN: permisos que faltaban (liquidaciones y facturas) --
        ("ADMIN", "liquidaciones:operar_grilla", "global"),
        ("ADMIN", "liquidaciones:calcular_cerrar", "global"),
        ("ADMIN", "facturas:gestionar", "global"),
        ("ADMIN", "periodos:gestionar", "global"),
        # -- FINANZAS --
        ("FINANZAS", "liquidaciones:ver", "global"),
        ("FINANZAS", "liquidaciones:gestionar", "global"),
    ]

    roles_table = sa.table(
        "roles",
        sa.column("id", postgresql.UUID),
        sa.column("codigo", sa.String),
        sa.column("tenant_id", postgresql.UUID),
    )
    rp_table = sa.table(
        "roles_permisos",
        sa.column("id", postgresql.UUID),
        sa.column("tenant_id", postgresql.UUID),
        sa.column("rol_id", postgresql.UUID),
        sa.column("permiso_id", postgresql.UUID),
        sa.column("habilitado", sa.Boolean),
        sa.column("alcance", sa.String),
        sa.column("created_at", sa.DateTime),
        sa.column("updated_at", sa.DateTime),
    )
    for rol_codigo, permiso_codigo, alcance in nuevas_asignaciones:
        op.execute(
            rp_table.insert().from_select(
                ["id", "tenant_id", "rol_id", "permiso_id", "habilitado", "alcance", "created_at", "updated_at"],
                sa.select(
                    sa.func.gen_random_uuid(),
                    sa.cast(sa.literal(SEED_TENANT_ID), postgresql.UUID),
                    roles_table.c.id,
                    permisos_table.c.id,
                    sa.true(),
                    sa.literal(alcance),
                    sa.func.now(),
                    sa.func.now(),
                ).where(
                    sa.and_(
                        roles_table.c.codigo == rol_codigo,
                        permisos_table.c.codigo == permiso_codigo,
                        roles_table.c.tenant_id == SEED_TENANT_ID,
                        permisos_table.c.tenant_id == SEED_TENANT_ID,
                    )
                ),
            )
        )


def downgrade() -> None:
    # Eliminar asignaciones nuevas
    permisos_nuevos_codes = [
        "calificaciones:ver", "equipos:ver", "equipos:gestionar",
        "avisos:ver", "avisos:gestionar", "tareas:ver",
        "encuentros:ver", "coloquios:ver", "liquidaciones:ver",
        "periodos:gestionar",
    ]
    for code in permisos_nuevos_codes:
        op.execute(
            "DELETE FROM roles_permisos WHERE permiso_id = (SELECT id FROM permisos WHERE codigo = '{}' AND tenant_id = '{}')".format(
                code, SEED_TENANT_ID
            )
        )
    # Eliminar asignaciones nuevas para ADMIN (liquidaciones/facturas)
    for code in ["liquidaciones:operar_grilla", "liquidaciones:calcular_cerrar", "facturas:gestionar"]:
        op.execute(
            "DELETE FROM roles_permisos WHERE permiso_id = (SELECT id FROM permisos WHERE codigo = '{}' AND tenant_id = '{}') AND rol_id = (SELECT id FROM roles WHERE codigo = 'ADMIN' AND tenant_id = '{}')".format(
                code, SEED_TENANT_ID, SEED_TENANT_ID
            )
        )
    # Eliminar permisos nuevos
    for code in permisos_nuevos_codes:
        op.execute(
            "DELETE FROM permisos WHERE codigo = '{}' AND tenant_id = '{}'".format(code, SEED_TENANT_ID)
        )
