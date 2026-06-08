"""c20 perfil y mensajeria interna — columnas de perfil + tablas de mensajeria

Revision ID: 20260608_0015
Revises: 20260608_0014
Create Date: 2026-06-08
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260608_0015"
down_revision: str | None = "20260608_0014"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ── Profile columns on usuarios ────────────────────────────────
    op.add_column("usuarios", sa.Column("regional", sa.String(length=100), nullable=True))
    op.add_column("usuarios", sa.Column("modalidad_cobro", sa.String(length=50), nullable=True))
    op.add_column("usuarios", sa.Column("genero", sa.String(length=50), nullable=True))
    op.add_column("usuarios", sa.Column("condicion_impositiva", sa.String(length=50), nullable=True))
    op.add_column("usuarios", sa.Column("matricula_profesional", sa.String(length=50), nullable=True))

    # ── HiloMensaje table ──────────────────────────────────────────
    op.create_table(
        "hilos_mensajes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("asunto", sa.String(length=255), nullable=False),
        sa.Column("participantes_ids", postgresql.JSONB, nullable=False),
        sa.Column("ultimo_mensaje_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_hilos_mensajes_tenant_id", "hilos_mensajes", ["tenant_id"])
    op.create_index(
        "ix_hilos_mensajes_participantes",
        "hilos_mensajes",
        ["participantes_ids"],
        postgresql_using="gin",
    )

    # ── MensajeInterno table ───────────────────────────────────────
    op.create_table(
        "mensajes_internos",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("hilo_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("remitente_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("cuerpo", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["hilo_id"], ["hilos_mensajes.id"]),
        sa.ForeignKeyConstraint(["remitente_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_mensajes_internos_hilo_id", "mensajes_internos", ["hilo_id"])
    op.create_index(
        "ix_mensajes_internos_hilo_created",
        "mensajes_internos",
        ["hilo_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_mensajes_internos_hilo_created", table_name="mensajes_internos")
    op.drop_index("ix_mensajes_internos_hilo_id", table_name="mensajes_internos")
    op.drop_table("mensajes_internos")
    op.drop_index("ix_hilos_mensajes_participantes", table_name="hilos_mensajes")
    op.drop_index("ix_hilos_mensajes_tenant_id", table_name="hilos_mensajes")
    op.drop_table("hilos_mensajes")
    op.drop_column("usuarios", "matricula_profesional")
    op.drop_column("usuarios", "condicion_impositiva")
    op.drop_column("usuarios", "genero")
    op.drop_column("usuarios", "modalidad_cobro")
    op.drop_column("usuarios", "regional")
