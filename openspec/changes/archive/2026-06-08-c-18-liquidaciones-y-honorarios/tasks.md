## 1. Safety Net, Governance and Discovery

- [x] 1.1 Read proposal, design, specs, `openspec/specs/liquidaciones-reglas-salariales/spec.md`, KB sections E17–E20, F10.1–F10.6 and FL-08.
- [x] 1.2 Confirm CRITICAL governance checkpoint with the user before writing production code.
- [x] 1.3 Run existing targeted backend tests for usuarios/asignaciones, estructura académica, RBAC and C-17 modules as Strict TDD safety net.
- [x] 1.4 Identify existing model/repository/service/router/test patterns for tenant-scoped financial or admin modules.

## 2. Data Model and Migration

- [x] 2.1 Write failing model/migration tests for `SalarioBase`, `SalarioPlus`, `MateriaPlus`, `Liquidacion`, `Factura` fields, tenant isolation, soft delete and constraints.
- [x] 2.2 Implement SQLAlchemy enums and models for roles/estado liquidación/estado factura following existing mixins and naming conventions.
- [x] 2.3 Implement `SalarioBase`, `SalarioPlus`, `MateriaPlus`, `Liquidacion` and `Factura` ORM models with tenant_id and indexes.
- [x] 2.4 Create one Alembic migration for C-18 tables, FKs, partial unique indexes, vigencia indexes and enum constraints.
- [x] 2.5 Run model/migration tests to green and triangulate cross-tenant, overlapping vigencia, soft-delete and closed snapshot cases.

## 3. Repository Layer

- [x] 3.1 Write failing repository tests for grilla salarial CRUD, lookup vigente by period, overlap detection and MateriaPlus mapping.
- [x] 3.2 Write failing repository tests for liquidaciones preview inputs, snapshot persistence, list/detail filters and duplicate close prevention.
- [x] 3.3 Write failing repository tests for factura CRUD, filters, state transitions and soft delete.
- [x] 3.4 Implement tenant-scoped grilla repositories with all queries filtered by `tenant_id` by default.
- [x] 3.5 Implement tenant-scoped liquidacion repositories for snapshots, historical listing and duplicate close checks.
- [x] 3.6 Implement tenant-scoped factura repository with filters by usuario, periodo, estado and date range.
- [x] 3.7 Run repository tests to green and triangulate active-only, cross-tenant, date-boundary and overlapping-vigencia cases.

## 4. Service Layer and Domain Rules

- [x] 4.1 Write failing service tests for salary grid validation, vigencia overlap prevention and MateriaPlus cross-tenant rejection.
- [x] 4.2 Write failing service tests for liquidation preview: base vigente, Plus accumulation by commission, materia without Plus, NEXO segment and facturante exclusion.
- [x] 4.3 Write failing service tests for close immutability, duplicate close rejection, audit event and closed snapshot preservation after grilla changes.
- [x] 4.4 Write failing service tests for factura registration, rejection of non-facturante, Pendiente→Abonada transition and invalid transitions.
- [x] 4.5 Implement grilla service methods with context validation and no direct DB access outside repositories.
- [x] 4.6 Implement liquidacion service calculation and close workflow with deterministic preview and immutable persisted snapshot.
- [x] 4.7 Implement factura service methods and state machine.
- [x] 4.8 Run service tests to green and triangulate missing base, missing Plus, missing bank data, facturante and NEXO scenarios.

## 5. API Schemas and Routers

- [x] 5.1 Write failing API tests for `/api/liquidaciones/grilla/*` covering CRUD, permission guards, invalid payloads and tenant isolation.
- [x] 5.2 Write failing API tests for `/api/liquidaciones/*` covering preview, close, list/detail, duplicate close, no-permission and cross-tenant rejection.
- [x] 5.3 Write failing API tests for `/api/facturas/*` covering create/list/detail/update/delete, mark abonada, invalid transition, no-permission and invalid payloads.
- [x] 5.4 Implement Pydantic v2 schemas with `ConfigDict(extra='forbid')`, no client-controlled `tenant_id`, typed dates/enums and decimal money fields.
- [x] 5.5 Implement grilla/liquidaciones/facturas routers wired to services, JWT dependencies and `require_permission(...)` guards.
- [x] 5.6 Register routers in the application using existing module conventions.
- [x] 5.7 Run API tests to green and triangulate permission, invalid payload, cross-tenant and closed-state scenarios.

## 6. Integration, Quality and Documentation

- [x] 6.1 Run all C-18 tests plus relevant existing backend suites with real PostgreSQL and record Strict TDD evidence.
- [x] 6.2 Verify Clean Architecture: no SQL queries in routers, no direct DB access in services, business rules outside routers.
- [x] 6.3 Verify CRITICAL-domain rules: identity from JWT, tenant isolation, RBAC fail-closed, audit on close, no hard delete.
- [x] 6.4 Verify source file size limits, Pydantic `extra='forbid'`, no DB mocks and migration downgrade safety.
- [x] 6.5 Update `CHANGES.md` C-18 status/scope if implementation deviates and document deviations for verify/archive.

### Verification notes 2026-06-08

- 6.1 passed with Docker PostgreSQL: `151 passed` for C-18, C-17, usuarios/asignaciones and RBAC suites.
- 6.2 passed after adding liquidaciones history filtering by segmento contable (`general`, `nexo`, `facturante`) with repository/service/API tests; C-18 routers/services pass Clean Architecture. Existing non-C18 services still contain direct SQL (`programa_service.py`, `fecha_academica_service.py`, `calificaciones.py`) and `health.py` executes SQL in a router.
- 6.3 passed for C-18: tenant and identity come from `CurrentUserDep`, endpoints use `require_permission(...)`, close writes `LIQUIDACION_CERRAR`, and deletes route through `soft_delete`.
- 6.4 passed for C-18: all checked files are <=500 LOC, schemas use `ConfigDict(extra="forbid")`, C-18 tests have no DB mocks, and migration `20260608_0014_c18_liquidaciones.py` defines downgrade.
- 6.5: `CHANGES.md` left unchanged because C-18 must remain pending until verify/archive; deviation to resolve before archive: add or explicitly de-scope liquidaciones history filtering by segmento contable from `openspec/changes/c-18-liquidaciones-y-honorarios/specs/liquidaciones-honorarios/spec.md`.
