## Verification Report: c-16-tareas-internas

**Date**: 2026-06-07
**Tasks**: 26/26 complete

### Test Results

Executed with `python:3.13-slim` on Docker network `activetracegestion_default`, using real PostgreSQL container `activetrace-c16-test-pg` and `DATABASE_URL=postgresql+asyncpg://trace:trace@activetrace-c16-test-pg:5432/trace_test`.

| Command | Result | Notes |
|---------|--------|-------|
| `pytest tests/test_tareas_internas.py tests/test_tareas_api.py -q` | PASS, 15/15 | C-16 model, repository, service and API tests passed. |
| `pytest tests/test_rbac.py tests/test_repositories_tenancy.py -q` | PASS, 26/26 | Initial attempt failed during fixture setup because the reused test schema contained dependent tables from prior runs; after `DROP SCHEMA public CASCADE; CREATE SCHEMA public;`, the requested safety tests passed. |

### Spec Compliance

| Requirement / Scenario | Status | Notes |
|------------------------|--------|-------|
| Crear tareas internas asignadas | PASS | `TareaService.create_task()` creates tasks through `TareaRepository.create()` with `tenant_id` from service context and default `Pendiente` state. |
| Alta de tarea con asignacion valida | PASS | `POST /api/tareas` uses `current_user.user_id` for `asignado_por`, validates same-tenant active assignee and optional materia, and rejects client-controlled `tenant_id`/`asignado_por` via `extra='forbid'`. |
| Rechazo de asignacion cross-tenant | PASS | `user_is_active()` and `materia_exists()` are tenant-scoped; cross-tenant assignee returns validation error and tests cover no creation. |
| Consultar mis tareas y administracion global | PASS | Separate `/api/tareas/mis` and `/api/tareas` endpoints exist, both guarded and tenant-scoped. |
| Mis tareas usa identidad de sesion | PASS | Router calls `list_my(current_user.user_id)` and exposes no external user identity parameter on `/mis`. |
| Listado global filtrable | PASS | Repository supports filters by `asignado_a`, `asignado_por`, `materia_id`, `estado` and free-text search, always with `Tarea.tenant_id == self.tenant_id`. |
| Delegar tareas con trazabilidad | PASS | `delegate_task()` validates actor and assignee, updates `asignado_a` and stores actor as `asignado_por`. |
| Delegacion exitosa | PASS | API and service tests cover delegation to a valid same-tenant active user. |
| Delegacion a usuario invalido | PASS | Service validates inactive/cross-tenant assignees before mutation; test confirms assignment remains unchanged for inactive user. |
| Gestionar workflow de estado | PASS | `EstadoTarea` defines required states and service-level `_allowed_transitions` enforces fail-closed transitions. |
| Transicion valida de progreso a resolucion | PASS | Service tests cover `Pendiente -> En progreso -> Resuelta`. |
| Transicion invalida desde estado terminal | PASS | Terminal states have empty transition sets; test covers rejection after `Resuelta`. |
| Comentarios en hilo de tarea | PASS | `ComentarioTarea` persists tenant, task, author, text and timestamps through base mixin. |
| Agregar comentario a tarea existente | PASS | `add_comment()` verifies task visibility in tenant and uses session `autor_id` from router. |
| Consultar hilo de comentarios | PASS | `get_detail()` attaches comments from `ComentarioTareaRepository.list_for_task()`, ordered by `created_at ASC` and tenant-scoped. |
| Proteger endpoints de tareas | PASS | Router is mounted at `/api/tareas`, all endpoints use `require_permission(TAREAS_GESTIONAR)` and `CurrentUserDep`. |
| Usuario sin permiso no accede | PASS | API test confirms 403 for authenticated user without `tareas:gestionar`. |
| Tenant siempre viene de la sesion | PASS | Service is instantiated with `current_user.tenant_id`; request schemas reject unknown identity/tenant body fields and router does not accept tenant overrides. |

### Design Coherence

- `Tarea` aggregate root with `ComentarioTarea` dependent: FOLLOWED. Tables, models and repositories keep comments dependent on a visible tenant-scoped task.
- Explicit fail-closed workflow: FOLLOWED. Allowed transitions are server-side and terminal states cannot transition.
- Separate `mis tareas` and global administration reads: FOLLOWED. `/mis` uses session identity; global list is filterable and tenant-scoped.
- Optional opaque academic context: FOLLOWED. `materia_id` is an optional FK with tenant validation; `contexto_id` is an optional opaque UUID.
- High-use indexes: FOLLOWED. Migration defines compound indexes for tenant/asignado/estado, tenant/asignador, tenant/materia, tenant/estado and tenant/updated_at, plus comment thread ordering.
- Identity and tenant from session: FOLLOWED. `current_user.user_id` and `current_user.tenant_id` are the only source for actor and tenant in router/service construction.
- No client-controlled `tenant_id` or `asignado_por`: FOLLOWED. Request schemas omit those fields and use `extra='forbid'`.
- Pydantic `extra='forbid'`: FOLLOWED. All request and response schemas in `app/schemas/tarea.py` define `ConfigDict(extra='forbid')`.
- Clean Architecture: FOLLOWED. Routers call services, services call repositories, and SQL queries are isolated in repositories.
- Tenant isolation and soft delete: FOLLOWED. `TenantScopedRepository.get/list/soft_delete` and task repositories filter by `tenant_id` and `deleted_at`.
- RBAC permission constant: FOLLOWED. `TAREAS_GESTIONAR = "tareas:gestionar"` exists and router uses it.

### Summary

- CRITICAL: None.
- WARNING: `TareaCreate.titulo` allows up to 255 characters while the DB column is `String(200)`, so titles between 201 and 255 characters can pass API validation and fail at persistence instead of returning schema validation.
- WARNING: The requested RBAC/tenancy safety suite needs a clean test schema when reused after C-16 tests; otherwise old dependent tables can make fixture teardown fail before assertions run.
- SUGGESTION: Add an API test for invalid terminal transition through `/api/tareas/{id}/estado`, not only at service level, to protect the HTTP error mapping.
- SUGGESTION: Consider narrowing `_registrar_auditoria()` exception handling to avoid swallowing unexpected audit model construction errors silently.

**Verdict**: READY FOR ARCHIVE
