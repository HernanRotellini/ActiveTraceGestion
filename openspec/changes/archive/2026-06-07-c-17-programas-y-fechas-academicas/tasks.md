## 1. Safety Net and Discovery

- [x] 1.1 Read proposal, design, specs, and relevant backend patterns for structure-academica, encuentros/coloquios and C-16 modules.
- [x] 1.2 Run existing targeted backend tests for shared structure/RBAC/repository patterns as Strict TDD safety net and record baseline.
  - Baseline: test_tareas_internas.py: 11 passed, test_tareas_api.py: 4 passed
  - Pre-existing: test_estructura_academica.py: 22 errors (DROP TABLE without CASCADE — unrelated to C-17)
- [x] 1.3 Confirm `estructura:gestionar` guard/dependency usage and router registration conventions.

## 2. Data Model and Migration

- [x] 2.1 Write failing model/migration tests for `ProgramaMateria` and `FechaAcademica` required fields, tenant isolation, FKs, soft delete, uniqueness and indexes.
- [x] 2.2 Implement SQLAlchemy models/enums for `ProgramaMateria`, `FechaAcademica` and `TipoFechaAcademica` following existing mixins and naming conventions.
- [x] 2.3 Create one Alembic migration for `programa_materia` and `fecha_academica`, including FKs, constraints and indexes by academic context.
- [x] 2.4 Run model/migration tests to green and triangulate duplicate, cross-tenant and soft-delete cases.

## 3. Repository Layer

- [x] 3.1 Write failing repository tests for create, get-by-id, update, soft-delete and filtered listings for programs and dates.
- [x] 3.2 Implement tenant-scoped repositories for programs and academic dates with all queries filtered by `tenant_id` by default.
- [x] 3.3 Add filters for programa by materia/carrera/cohorte and fechas by materia/cohorte/tipo/periodo/date range.
- [x] 3.4 Run repository tests to green and triangulate active-only, cross-tenant and calendar range queries.

## 4. Service Layer and Domain Rules

- [x] 4.1 Write failing service tests for context validation, opaque file references, duplicate prevention, CRUD and LMS fragment generation.
- [x] 4.2 Implement program service methods for create, list, detail, update and soft-delete with same-tenant context validation.
- [x] 4.3 Implement academic date service methods for create, list, calendar list, detail, update and soft-delete with duplicate prevention.
- [x] 4.4 Implement deterministic LMS fragment generation for filtered academic dates, including empty-state behavior.
- [x] 4.5 Run service tests to green and triangulate valid, invalid context, duplicate and no-dates scenarios.

## 5. API Schemas and Routers

- [x] 5.1 Write failing API tests for `/api/programas` covering auth, permission guard, create/list/detail/update/delete, invalid payload and cross-tenant rejection.
- [x] 5.2 Write failing API tests for `/api/fechas-academicas` covering CRUD, tabular filters, calendar range, LMS fragment, invalid payload and permission failures.
- [x] 5.3 Implement Pydantic v2 schemas with `ConfigDict(extra='forbid')`, no client-controlled `tenant_id`, and typed enums/dates.
- [x] 5.4 Implement FastAPI routers `/api/programas` and `/api/fechas-academicas` wired to services, JWT dependencies and `require_permission("estructura:gestionar")`.
- [x] 5.5 Register routers in the application using existing module conventions.
- [x] 5.6 Run API tests to green and triangulate forbidden/no-permission, cross-tenant and invalid payload scenarios.

## 6. Integration, Quality and Documentation

- [x] 6.1 Run relevant backend test suites with real PostgreSQL and record Strict TDD evidence for every task group.
  - 85 tests passed across all suites (C-17 models: 13, repos: 14, services: 20, API: 23, tareas existing: 15). Zero regressions.
- [x] 6.2 Verify Clean Architecture boundaries: no queries outside repositories, no business logic in routers, no direct DB access in services.
  - ✅ All queries in repositories only; services only call repo methods; routers only call services.
- [x] 6.3 Verify backend file size limits, Pydantic `extra='forbid'`, tenant isolation, soft delete and no DB mocks.
  - ✅ All source files < 200 LOC (well under 500 limit). All schemas have extra='forbid'. All repos filter by tenant_id. Soft delete everywhere. No DB mocks — all real PostgreSQL.
- [x] 6.4 Update task checkboxes as implementation completes and document any deviations/open questions for verify/archive.
  - See deviations below.
