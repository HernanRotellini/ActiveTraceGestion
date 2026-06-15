## Why

Las migraciones `20260602_0003_rbac_foundation` y `20260613_0001_fix_frontend_permissions` contienen el seed de roles, permisos y asignaciones rol-permiso. Ambas fueron *stamped* como aplicadas sin ejecutarse (por `alembic stamp head`), por lo que las tablas `roles`, `permisos` y `roles_permisos` están vacías para el tenant semilla. Cada endpoint verifica permisos contra estas tablas → **403 Forbidden en todas las pantallas del frontend**, incluso para el rol ADMIN.

## What Changes

- Insertar los 7 roles del dominio: ALUMNO, TUTOR, PROFESOR, COORDINADOR, NEXO, ADMIN, FINANZAS.
- Insertar los 32 permisos totales (23 originales + 9 de la migración de permisos de lectura).
- Insertar las ~76 asignaciones rol-permiso con sus alcances (global/propio).
- Todo debe ser **idempotente**: si el dato ya existe, no duplicarlo.
- No hay cambios de schema — solo seed data faltante.

## Capabilities

### New Capabilities

Ninguna. Este cambio no introduce nuevas capacidades, solo materializa datos que debieron existir desde las migraciones.

### Modified Capabilities

Ninguna. Este cambio no modifica requerimientos de capacidades existentes.

## Impact

- **Script**: `backend/scripts/seed_rbac.py` — script idempotente ejecutable a demanda.
- **Base de datos**: tablas `roles`, `permisos`, `roles_permisos` del tenant `UTN_MENDOZA_GLOBAL`.
- **Seed principal**: Eventualmente integrarse en `seed_dev_data.py` (alcance futuro, fuera de este change).
