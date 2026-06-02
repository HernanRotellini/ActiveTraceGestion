## 1. Migration

- [x] 1.1 Create Alembic migration 004: `carreras`, `cohortes`, `materias` tables with composite unique indexes and FKs

## 2. Models

- [x] 2.1 Create `backend/app/models/estructura_academica.py` with `Carrera`, `Cohorte`, `Materia` ORM models extending `TenantScopedMixin`

## 3. Schemas

- [x] 3.1 Create `backend/app/schemas/estructura_academica.py` with Pydantic request/response DTOs for all three entities (`extra='forbid'`, `from_attributes=True`)

## 4. Repositories

- [x] 4.1 Create `backend/app/repositories/estructura_academica.py` with `CarreraRepository`, `CohorteRepository`, `MateriaRepository` extending `TenantScopedRepository`; include uniqueness lookup methods and `get_by_codigo` / `get_by_carrera_id`

## 5. Service

- [x] 5.1 Create `backend/app/services/estructura_academica.py` with `EstructuraAcademicaService` implementing CRUD + business rules (uniqueness validation, inactive carrera blocks cohorte creation)

## 6. Router

- [x] 6.1 Create `backend/app/api/v1/routers/estructura_academica.py` with endpoints at `/api/admin/carreras`, `/api/admin/cohortes`, `/api/admin/materias`, all guarded by `require_permission(ESTRUCTURA_GESTIONAR)`
- [x] 6.2 Wire the new router into the app's router registry

## 7. Tests

- [x] 7.1 Write tests for Carrera CRUD (create, list, update, soft delete, duplicate codigo, multi-tenant isolation)
- [x] 7.2 Write tests for Cohorte CRUD (create, duplicate name, inactive carrera block, list by carrera, multi-tenant isolation)
- [x] 7.3 Write tests for Materia CRUD (create, duplicate codigo, multi-tenant isolation)
- [x] 7.4 Write test for authorization guard (403 without `estructura:gestionar`)

## 8. Verification

- [x] 8.1 Run full test suite and confirm ≥80% line coverage
- [x] 8.2 Run lint and type checks (no lint tools available in project; modules import correctly)
