## 1. Models and Migration

- [x] 1.1 Create `backend/app/models/rbac.py` with models: Rol, Permiso, RolPermiso (all TenantScopedMixin)
- [x] 1.2 Create Alembic migration 003 with tables `rol`, `permiso`, `rol_permiso`
- [x] 1.3 Add seed data to migration 003: 7 roles (ALUMNO, TUTOR, PROFESOR, COORDINADOR, NEXO, ADMIN, FINANZAS)
- [x] 1.4 Add seed data to migration 003: all permission codes (`modulo:accion`) from the matrix
- [x] 1.5 Add seed data to migration 003: all role-permission assignments from 03_actores_y_roles.md §3.3 matrix

## 2. Repository

- [x] 2.1 Create `backend/app/repositories/rbac.py` with `RolRepository` (list, get_by_code, CRUD)
- [x] 2.2 Add `PermisoRepository` (list, get_by_code, CRUD)
- [x] 2.3 Add `RolPermisoRepository` (get_permisos_efectivos by role codes)
- [x] 2.4 Implement `PermissionResolver` as a stateless service that queries effective permissions for a set of role codes scoped by tenant

## 3. Authorization Guard

- [x] 3.1 Create `backend/app/services/authorization.py` with `AuthorizationService.effective_permissions(user_id, tenant_id) -> set[str]`
- [x] 3.2 Implement `require_permission` class-based FastAPI dependency in `backend/app/core/dependencies.py`
- [x] 3.3 Create `backend/app/models/permisos.py` with typed permission constants (e.g., `CALIFICACIONES_IMPORTAR = "calificaciones:importar"`)
- [x] 3.4 Add permission resolution error handling: 403 with audit-worthy detail, 401 if not authenticated

## 4. API Router for Admin Catalog

- [x] 4.1 Create `backend/app/schemas/rbac.py` with Pydantic schemas: RolResponse, PermisoResponse, RolPermisoResponse
- [x] 4.2 Create `backend/app/api/v1/routers/rbac.py` with admin CRUD endpoints for rol, permiso, rol_permiso (protected with ADMIN role)
- [x] 4.3 Wire router in app factory

## 5. Tests

- [x] 5.1 Write Safety Net test: run existing tests to establish baseline
- [x] 5.2 Write test: authenticated user without permission gets 403
- [x] 5.3 Write test: authenticated user with permission gets 200
- [x] 5.4 Write test: union of roles produces combined permissions
- [x] 5.5 Write test: unauthenticated request gets 401 before permission check
- [x] 5.6 Write test: permission `(propio)` flag is recognized as semantic convention
- [x] 5.7 Write test: catalog is administrable (add new role, assign permission, verify)
