## 1. Safety Net and Discovery

- [x] 1.1 Read proposal, design, specs, and current backend patterns for existing domain modules before implementation.
- [x] 1.2 Run the existing targeted backend tests for shared auth/RBAC/repository patterns as a Strict TDD safety net and record the baseline.
- [x] 1.3 Confirm whether `tareas:gestionar` exists in RBAC seed/matrix and decide whether C-16 must add it.

## 2. Data Model and Migration

- [x] 2.1 Write failing model/migration tests for `Tarea` and `ComentarioTarea` tenant isolation, required fields, relationships, soft delete and indexes.
- [x] 2.2 Implement SQLAlchemy models/enums for `Tarea` and `ComentarioTarea` following existing base mixins and naming conventions.
- [x] 2.3 Create one Alembic migration for `tarea` and `comentario_tarea`, including FKs, constraints and high-use query indexes.
- [x] 2.4 Run migration/model tests to green and triangulate cross-tenant and soft-delete cases.

## 3. Repository Layer

- [x] 3.1 Write failing repository tests for create, get-by-id, list-my, list-global filters, delegation update and comment retrieval with real PostgreSQL.
- [x] 3.2 Implement tenant-scoped repositories for tasks and task comments with all queries isolated by `tenant_id` by default.
- [x] 3.3 Add pagination/order handling consistent with existing repository patterns for high-use listings.
- [x] 3.4 Run repository tests to green and triangulate filters by asignado, asignador, materia, estado and búsqueda libre.

## 4. Service Layer and Workflow Rules

- [x] 4.1 Write failing service tests for task creation using session actor, delegation, valid/invalid state transitions and comments.
- [x] 4.2 Implement task service methods for create, my tasks, global list, detail, delegate, change status and add comment.
- [x] 4.3 Enforce allowed transitions `Pendiente → En progreso/Cancelada` and `En progreso → Resuelta/Cancelada`, rejecting terminal-state changes.
- [x] 4.4 Validate same-tenant users/materias and reject cross-tenant or inactive assignees without mutating existing tasks.
- [x] 4.5 Run service tests to green and triangulate happy path plus invalid transition/cross-tenant cases.

## 5. API Schemas and Router

- [x] 5.1 Write failing API tests for `/api/tareas/*` covering auth, permission guard, identity from JWT, create/list/detail/delegate/status/comment endpoints and validation errors.
- [x] 5.2 Implement Pydantic v2 request/response schemas with `ConfigDict(extra='forbid')` and no client-controlled `tenant_id` or `asignado_por`.
- [x] 5.3 Implement FastAPI router `/api/tareas/*` wired to services, JWT dependencies and `require_permission("tareas:gestionar")`.
- [x] 5.4 Add router registration to the application using existing module conventions.
- [x] 5.5 Run API tests to green and triangulate forbidden/no-permission, cross-tenant and invalid payload scenarios.

## 6. Integration, Quality and Documentation

- [x] 6.1 Add or update RBAC seed/migration for `tareas:gestionar` only if discovery confirms it is missing.
- [x] 6.2 If audit helper exists, register significant actions for task create, delegation and state change without blocking if audit is unavailable.
- [x] 6.3 Run the relevant backend test suite with real PostgreSQL and record Strict TDD evidence for every task group.
- [x] 6.4 Verify backend file size limits, no DB mocks, no business logic in routers, no direct DB access in services and Pydantic `extra='forbid'`.
- [x] 6.5 Update task checkboxes as implementation completes and document any deviations/open questions for archive/verify.
