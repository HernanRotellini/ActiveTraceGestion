## Context

Las migraciones `20260602_0003_rbac_foundation` y `20260613_0001_fix_frontend_permissions` fueron creadas con `alembic stamp head` sin ejecutar su contenido DML (INSERTs). Como resultado, las tablas `roles`, `permisos` y `roles_permisos` existen pero están vacías para el tenant `UTN_MENDOZA_GLOBAL`.

El sistema RBAC usa una matriz `rol → permiso → alcance` que se verifica en cada endpoint mediante `require_permission(...)`. Sin registros en `roles_permisos`, toda verificación devuelve 403.

Las dos migraciones juntas definen:
- **7 roles**: ALUMNO, TUTOR, PROFESOR, COORDINADOR, NEXO, ADMIN, FINANZAS
- **32 permisos**: 23 originales + 9 de la migración de permisos de lectura
- **~76 asignaciones**: combinaciones rol-permiso con alcances `global` o `propio`

## Goals / Non-Goals

**Goals:**
- Script idempotente que inserte todos los roles, permisos y asignaciones faltantes.
- Ejecutable desde CLI con `docker compose exec api python scripts/seed_rbac.py`.
- Compatible con el tenant `UTN_MENDOZA_GLOBAL` (UUID `00000000-0000-0000-0000-000000000001`).

**Non-Goals:**
- No modificar el schema de la base de datos (solo DML).
- No modificar migraciones existentes.
- No cubrir multi-tenancy (solo el tenant seed).
- No integrar en `seed_dev_data.py` (se hará en otro change).

## Decisions

| Decisión | Opción elegida | Alternativas | Razón |
|----------|---------------|-------------|-------|
| Formato del script | Script Python independiente | Modificar migraciones existentes | Las migraciones están *stamped* como aplicadas. Revertirlas y re-ejecutarlas sería destructivo (dropearía tablas). |
| Idempotencia | `INSERT ... ON CONFLICT DO NOTHING` usando unique constraint | `SELECT` previo | El modelo tiene `UniqueConstraint("tenant_id", "codigo")` en roles y permisos, y `UniqueConstraint("rol_id", "permiso_id")` en roles_permisos. `ON CONFLICT DO NOTHING` es más limpio y rápido. |
| UUIDs | Usar `gen_random_uuid()` | UUIDs fijos | Las migraciones originales usan `gen_random_uuid()`. Mantener consistencia. |
| Alcance | Columna `alcance` con valores `global` / `propio` | — | Definido por el modelo existente. |
| Ubicación | `backend/scripts/seed_rbac.py` | — | Convención del proyecto (`scripts/`). |

## Risks / Trade-offs

- **[Idempotencia parcial]** Si un rol existe pero le faltan permisos, el script los agrega. Pero si un permiso existe y su asignación también, `ON CONFLICT` la salta correctamente.
- **[Multi-tenancy]** El script solo cubre el tenant seed. Para nuevos tenants, la creación debe incluir la matriz completa de permisos. Esto es responsabilidad del módulo de provisioning, fuera de este change.
- **[Migrations vs scripts]** Idealmente este seed viviría en migraciones. Pero como las migraciones ya están *stamped*, un script es la solución pragmática. Cuando se refactorice el sistema de migraciones, este script podría integrarse.

## Open Questions

Ninguna. La matriz de permisos está completamente definida en las dos migraciones mencionadas.
