## Why

El sistema actual autentica usuarios (C-03) pero no autoriza acciones. Sin un sistema de RBAC con permisos finos, cualquier usuario autenticado puede acceder a cualquier endpoint. Esto es inviable para un sistema multi-tenant con 7 roles del dominio (ALUMNO, TUTOR, PROFESOR, COORDINADOR, NEXO, ADMIN, FINANZAS) que necesitan capacidades drásticamente distintas. Cada endpoint debe declarar el permiso que exige y el framework debe denegar acceso si el usuario no lo tiene, con resolución server-side por request.

## What Changes

- Nuevos modelos: `Rol`, `Permiso`, `RolPermiso` (catálogo administrable como datos, NO hardcode)
- Seed de la matriz base: 7 roles del dominio con sus permisos según 03_actores_y_roles.md §3.3
- Servicio de resolución de permisos efectivos (unión de roles, acotada por tenant)
- Dependency `require_permission("modulo:accion")` para decorar endpoints
- Migración 003 con tablas + seed
- Tests de cobertura: 403 sin permiso, unión de roles, permiso (propio) vs global

## Capabilities

### New Capabilities
- `rbac-core`: Gestión de roles, permisos y matriz rol-permiso como catálogo administrable. Resolución de permisos efectivos del usuario autenticado en cada request.
- `authorization-guard`: Dependency `require_permission` que permite a cada endpoint declarar el permiso que exige y produce 403 si el usuario no lo tiene.

### Modified Capabilities
- `user-authentication`: El flujo de login (C-03) ya resuelve `CurrentUser` con roles; C-04 agrega la resolución de permisos efectivos a partir de esos roles y el guard que los evalúa.

## Impact

- Archivos nuevos: `backend/app/models/rbac.py`, `backend/app/repositories/rbac.py`, `backend/app/services/authorization.py`, `backend/app/schemas/rbac.py`, `backend/app/api/v1/routers/rbac.py`
- Archivos modificados: `backend/app/core/dependencies.py` (agregar `require_permission`)
- Migración nueva: Alembic 003 con tablas `rol`, `permiso`, `rol_permiso` + seed de matriz base
- Tests nuevos: `backend/tests/test_rbac.py`
- Auditoría: integración con C-05 (futuro) para auditar denegaciones y cambios en la matriz
