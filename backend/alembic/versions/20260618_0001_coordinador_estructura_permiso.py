"""grant estructura:gestionar to COORDINADOR

Revision ID: 20260618_0001
Revises: 20260615_0002
Create Date: 2026-06-18
"""

from collections.abc import Sequence

from alembic import op

revision: str = "20260618_0001"
down_revision: str | None = "20260615_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO roles_permisos (
            id,
            tenant_id,
            rol_id,
            permiso_id,
            habilitado,
            alcance,
            created_at,
            updated_at
        )
        SELECT
            gen_random_uuid(),
            r.tenant_id,
            r.id,
            p.id,
            true,
            'global',
            now(),
            now()
        FROM roles r
        JOIN permisos p
            ON p.tenant_id = r.tenant_id
            AND p.codigo = 'estructura:gestionar'
            AND p.deleted_at IS NULL
        WHERE r.codigo = 'COORDINADOR'
            AND r.deleted_at IS NULL
            AND NOT EXISTS (
                SELECT 1
                FROM roles_permisos rp
                WHERE rp.tenant_id = r.tenant_id
                    AND rp.rol_id = r.id
                    AND rp.permiso_id = p.id
                    AND rp.deleted_at IS NULL
            )
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DELETE FROM roles_permisos rp
        USING roles r, permisos p
        WHERE rp.rol_id = r.id
            AND rp.permiso_id = p.id
            AND r.codigo = 'COORDINADOR'
            AND p.codigo = 'estructura:gestionar'
        """
    )
