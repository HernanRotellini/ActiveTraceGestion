## 1. Models and Migration

- [x] 1.1 Create `backend/app/models/audit_log.py` with `AuditLog` model: id (UUID PK), tenant_id (FK), fecha_hora, actor_id, impersonado_id (nullable), materia_id (nullable), accion (string), detalle (JSONB), filas_afectadas (integer), ip (string), user_agent (string). Inherits `UuidPrimaryKeyMixin` directly (not TenantScopedMixin — no updated_at/deleted_at for append-only). No updated_at, no deleted_at columns.
- [x] 1.2 Add complete audit action code constants to `backend/app/models/permisos.py`: CALIFICACIONES_IMPORTAR, PADRON_CARGAR, COMUNICACION_ENVIAR, COMUNICACION_APROBAR, COMUNICACION_CANCELAR, ASIGNACION_MODIFICAR, LIQUIDACION_CERRAR, IMPERSONACION_INICIAR, IMPERSONACION_FINALIZAR
- [x] 1.3 Create Alembic migration `20260607_0014_audit_log.py` (revision `20260607_0014`, down_revision `20260607_0013`) with CREATE TABLE `audit_log`, CREATE FUNCTION `reject_audit_log_modification()`, CREATE TRIGGER `audit_log_append_only_before_update` and `audit_log_append_only_before_delete` that raise exception on UPDATE/DELETE
- [x] 1.4 Export `AuditLog` in `backend/app/models/__init__.py`

## 2. Repository

- [x] 2.1 Create `backend/app/repositories/audit_log.py` with `AuditLogRepository`: `create(entry) -> AuditLog` and `list(filters) -> list[AuditLog]`. NO update/delete methods. Filters: tenant_id (required), fecha_desde, fecha_hasta, actor_id, accion, materia_id, limit, offset.

## 3. Audit Service

- [x] 3.1 Extend `CurrentUser` in `backend/app/services/auth.py` with optional `impersonator_id: UUID | None` field. When impersonator_id is set, the session is under impersonation and actions are attributed to the impersonator.
- [x] 3.2 Create `backend/app/services/audit.py` with `AuditService`: constructor receives `db` (AsyncSession), `current_user` (CurrentUser), `ip` (str), `user_agent` (str). Method `log(accion, detalle, filas_afectadas, materia_id=None) -> AuditLog`. Typed helper methods per action code (e.g., `log_calificaciones_importar(total_filas, detalle_extra=None)`).
- [x] 3.3 Add `get_audit_service` dependency in `backend/app/core/dependencies.py` that extracts IP/user-agent from request, reads current_user, and returns an AuditService instance.

## 4. API Router

- [x] 4.1 Create `backend/app/schemas/audit.py` with Pydantic schemas: `AuditLogResponse`, `AuditLogListResponse`, `AuditLogFilter` (query params)
- [x] 4.2 Create `backend/app/api/v1/routers/audit.py` with `GET /api/v1/audit/logs` endpoint, protected with `require_permission("auditoria:ver")`, scoped by tenant. Supports filters: fecha_desde, fecha_hasta, actor_id, accion, materia_id. Paginated response.
- [x] 4.3 Wire audit router in app factory

## 5. Tests

- [x] 5.1 Write Safety Net test: run existing tests to establish baseline
- [x] 5.2 Write test: insert audit entry succeeds with all required fields
- [x] 5.3 Write test: update audit entry is rejected at app level (repository has no update)
- [x] 5.4 Write test: delete audit entry is rejected at app level (repository has no delete)
- [x] 5.5 Write test: audit entry under impersonation records actor_id as impersonator and impersonado_id as target
- [x] 5.6 Write test: audit entry without impersonation has impersonado_id = None
- [x] 5.7 Write test: query audit log filtered by date range returns correct entries
- [x] 5.8 Write test: query audit log is scoped by tenant (user from tenant A cannot see entries from tenant B)
- [x] 5.9 Write test: unauthenticated request to query endpoint returns 401
- [x] 5.10 Write test: user without `auditoria:ver` permission gets 403 on query endpoint
