"""add unique active carrera nombre per tenant

Revision ID: 20260618_0002
Revises: 20260618_0001
Create Date: 2026-06-18
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260618_0002"
down_revision: str | None = "20260618_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        "uq_carreras_tenant_nombre_active",
        "carreras",
        ["tenant_id", "nombre"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index("uq_carreras_tenant_nombre_active", table_name="carreras")
