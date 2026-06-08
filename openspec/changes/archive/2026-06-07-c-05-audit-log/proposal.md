## Why

El sistema actual no registra trazabilidad de acciones significativas (importación de calificaciones, envío de comunicaciones, modificaciones de equipos docentes, etc.). Sin un audit-log append-only, es imposible rastrear quién hizo qué, cuándo y bajo qué contexto — incluyendo acciones realizadas bajo impersonación. Esto es un requisito regulatorio y de auditoría para una plataforma multi-tenant que gestiona datos académicos y financieros sensibles. Cada acción crítica debe ser inmodificable y trazable.

## What Changes

- Nuevo modelo `AuditLog` append-only en DB: sin UPDATE ni DELETE a nivel app ni DB (triggers/restricciones). Campos: actor_id, impersonado_id, tenant_id, materia_id, accion (código estandarizado), detalle (JSON), filas_afectadas, ip, user_agent, fecha_hora.
- Helper/decorator/servicio de auditoría para registrar acciones desde los servicios del dominio con códigos estandarizados (`CALIFICACIONES_IMPORTAR`, `PADRON_CARGAR`, `COMUNICACION_ENVIAR`, etc.).
- Soporte de impersonación: sesión distinguible vía `CurrentUser`, acciones atribuidas al ACTOR REAL, registro de eventos `IMPERSONACION_INICIAR` / `IMPERSONACION_FINALIZAR`.
- Catálogo ampliado de códigos de acción en `permisos.py`.
- Migración 0014: tabla `audit_log`.
- Tests: append-only (update/delete rechazados), atribución bajo impersonación, registro con código + filas afectadas, códigos de acción estándar.

## Capabilities

### New Capabilities
- `audit-trail`: Registro inmutable y trazable de acciones significativas del sistema, con códigos estandarizados, soporte de impersonación y consulta de historial.

### Modified Capabilities
- `rbac-core`: Agregar permiso `impersonacion:usar` (ya definido como constante en permisos.py) como requisito para iniciar impersonación, vinculado al registro de auditoría.

## Impact

- Archivo nuevo: `backend/app/models/audit_log.py`
- Archivo nuevo: `backend/app/repositories/audit_log.py`
- Archivo nuevo: `backend/app/services/audit.py` (servicio + helper para registrar acciones)
- Archivo nuevo: `backend/app/schemas/audit.py` (Pydantic schemas)
- Archivo nuevo: `backend/app/api/v1/routers/audit.py` (consulta de auditoría)
- Archivo modificado: `backend/app/models/permisos.py` (catálogo completo de códigos de acción)
- Archivo modificado: `backend/app/core/security.py` o dependencias (impersonación distinguible)
- Archivo modificado: `backend/app/models/__init__.py` (exportar AuditLog)
- Migración nueva: Alembic `20260607_0014_audit_log`
- Tests nuevos: `backend/tests/test_audit.py`
