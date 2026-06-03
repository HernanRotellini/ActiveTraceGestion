## 1. Migration

- [x] 1.1 Create Alembic migration 005: `usuarios` table with encrypted PII columns, `email_hash` for deterministic lookup; `asignaciones` table with FKs to usuarios, carreras, cohortes, materias

## 2. Models

- [x] 2.1 Create `backend/app/models/usuarios_asignaciones.py` with `Usuario` ORM model (tenant-scoped, PII fields, email_hash, estado, legajo, banco, facturador) and `Asignacion` ORM model (usuario_id, rol, contexto académico, vigencia)

## 3. Schemas

- [x] 3.1 Create `backend/app/schemas/usuarios.py` with Pydantic request/response DTOs (UsuarioCreate, UsuarioUpdate, UsuarioResponse with `extra='forbid'`, `from_attributes=True`)
- [x] 3.2 Create `backend/app/schemas/asignaciones.py` with Pydantic request/response DTOs (AsignacionCreate, AsignacionUpdate, AsignacionResponse with `estado_vigencia` computed field)

## 4. Repositories

- [x] 4.1 Create `backend/app/repositories/usuarios.py` with `UsuarioRepository` extending `TenantScopedRepository[Usuario]`; PII encryption/decryption, `get_by_email` via `email_hash`, `set_committed_value` to prevent auto-flush
- [x] 4.2 Create `backend/app/repositories/asignaciones.py` with `AsignacionRepository` extending `TenantScopedRepository[Asignacion]`; filter methods `list_by_materia`, `list_by_usuario`, `list_by_rol`

## 5. Services

- [x] 5.1 Create `backend/app/services/usuarios.py` with `UsuarioService` implementing CRUD + email uniqueness, activate/deactivate, `DuplicateEmailError`, `NotFoundError`
- [x] 5.2 Create `backend/app/services/asignaciones.py` with `AsignacionService` implementing CRUD + vigencia validation, responsable existence check, multi-rol support

## 6. Routers

- [x] 6.1 Create `backend/app/api/v1/routers/usuarios.py` with endpoints at `/api/admin/usuarios` (POST, GET list, GET by id, PATCH, DELETE), guarded by `require_permission(USUARIOS_GESTIONAR)`
- [x] 6.2 Create `backend/app/api/v1/routers/asignaciones.py` with endpoints at `/api/asignaciones` (POST, GET list with filter query params, GET by id, PATCH, DELETE), guarded by `require_permission(EQUIPOS_ASIGNAR)`
- [x] 6.3 Wire both new routers into the app's router registry in `main.py`

## 7. Tests

- [x] 7.1 Tests for Usuario CRUD (create, list, get, update, soft delete, duplicate email, same email different tenant, multi-tenant isolation)
- [x] 7.2 Tests for PII encryption (ciphertext stored ≠ plaintext, plaintext returned in response)
- [x] 7.3 Tests for Asignacion CRUD (create with full context, global role, responsable, list, filter by materia, soft delete)
- [x] 7.4 Tests for vigencia (expired → `vencida`, active → `vigente`, no end date → `vigente`)
- [x] 7.5 Tests for multi-rol support (single user with PROFESOR + COORDINADOR)
- [x] 7.6 Tests for authorization guards (403 without `usuarios:gestionar`, 403 without `equipos:asignar`)

## 8. Verification

- [x] 8.1 Full test suite: 152/154 pass (2 pre-existing migration test failures), 26/26 C-07 pass
- [x] 8.2 Run lint and type checks (skipped: no lint tools installed in project — C-01 foundation didn't include them)
