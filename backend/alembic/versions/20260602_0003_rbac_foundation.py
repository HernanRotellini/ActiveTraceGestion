"""rbac foundation — roles, permissions, assignment matrix

Revision ID: 20260602_0003
Revises: 20260602_0002
Create Date: 2026-06-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260602_0003"
down_revision: str | None = "20260602_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# ── Seed tenant UUID (used as reference for base matrix) ──────
SEED_TENANT_ID = "00000000-0000-0000-0000-000000000001"


def upgrade() -> None:
    # ── Tables ────────────────────────────────────────────────
    op.create_table(
        "roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("codigo", sa.String(length=100), nullable=False),
        sa.Column("nombre", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "codigo", name="uq_roles_tenant_codigo"),
    )
    op.create_index("ix_roles_tenant_id", "roles", ["tenant_id"])
    op.create_index("ix_roles_codigo", "roles", ["codigo"])

    op.create_table(
        "permisos",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("codigo", sa.String(length=100), nullable=False),
        sa.Column("nombre", sa.String(length=255), nullable=False),
        sa.Column("modulo", sa.String(length=100), nullable=False),
        sa.Column("accion", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "codigo", name="uq_permisos_tenant_codigo"),
    )
    op.create_index("ix_permisos_tenant_id", "permisos", ["tenant_id"])
    op.create_index("ix_permisos_codigo", "permisos", ["codigo"])

    op.create_table(
        "roles_permisos",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rol_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("permiso_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("habilitado", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("alcance", sa.String(length=20), server_default="global", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["rol_id"], ["roles.id"]),
        sa.ForeignKeyConstraint(["permiso_id"], ["permisos.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("rol_id", "permiso_id", name="uq_roles_permisos_rol_permiso"),
    )
    op.create_index("ix_roles_permisos_tenant_id", "roles_permisos", ["tenant_id"])
    op.create_index("ix_roles_permisos_rol_id", "roles_permisos", ["rol_id"])
    op.create_index("ix_roles_permisos_permiso_id", "roles_permisos", ["permiso_id"])

    # ── Seed: roles (7) ───────────────────────────────────────
    roles_codes_nombres = [
        ("ALUMNO", "Alumno"),
        ("TUTOR", "Tutor"),
        ("PROFESOR", "Profesor"),
        ("COORDINADOR", "Coordinador"),
        ("NEXO", "Nexo"),
        ("ADMIN", "Administrador"),
        ("FINANZAS", "Finanzas"),
    ]
    roles_table = sa.table(
        "roles",
        sa.column("id", postgresql.UUID),
        sa.column("tenant_id", postgresql.UUID),
        sa.column("codigo", sa.String),
        sa.column("nombre", sa.String),
        sa.column("created_at", sa.DateTime),
        sa.column("updated_at", sa.DateTime),
    )
    for codigo, nombre in roles_codes_nombres:
        op.execute(
            roles_table.insert().values(
                id=sa.func.gen_random_uuid(),
                tenant_id=SEED_TENANT_ID,
                codigo=codigo,
                nombre=nombre,
                created_at=sa.func.now(),
                updated_at=sa.func.now(),
            )
        )

    # ── Seed: permisos (21) ───────────────────────────────────
    permisos_list = [
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
    for codigo, nombre, modulo, accion in permisos_list:
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

    # ── Seed: role-permission assignments ─────────────────────
    # Matriz de 03_actores_y_roles.md §3.3
    # Formato: (rol_codigo, permiso_codigo, alcance)
    matrix = [
        ("ALUMNO", "academico:ver_estado_propio", "global"),
        ("ALUMNO", "evaluaciones:reservar", "global"),
        ("TUTOR", "avisos:confirmar", "global"),
        ("TUTOR", "atrasados:ver", "global"),
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
        ("FINANZAS", "avisos:confirmar", "global"),
        ("FINANZAS", "auditoria:ver", "global"),
        ("FINANZAS", "liquidaciones:operar_grilla", "global"),
        ("FINANZAS", "liquidaciones:calcular_cerrar", "global"),
        ("FINANZAS", "facturas:gestionar", "global"),
    ]

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
    for rol_codigo, permiso_codigo, alcance in matrix:
        op.execute(
            rp_table.insert().from_select(
                ["id", "tenant_id", "rol_id", "permiso_id", "habilitado", "alcance", "created_at", "updated_at"],
                sa.select(
                    sa.func.gen_random_uuid(),
                    sa.literal(SEED_TENANT_ID),
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
    op.drop_index("ix_roles_permisos_permiso_id", table_name="roles_permisos")
    op.drop_index("ix_roles_permisos_rol_id", table_name="roles_permisos")
    op.drop_index("ix_roles_permisos_tenant_id", table_name="roles_permisos")
    op.drop_table("roles_permisos")
    op.drop_index("ix_permisos_codigo", table_name="permisos")
    op.drop_index("ix_permisos_tenant_id", table_name="permisos")
    op.drop_table("permisos")
    op.drop_index("ix_roles_codigo", table_name="roles")
    op.drop_index("ix_roles_tenant_id", table_name="roles")
    op.drop_table("roles")
