## Context

El proyecto activia-trace requiere un audit-log inmutable para registrar acciones significativas del sistema. Actualmente no existe trazabilidad de operaciones como importación de calificaciones, envío de comunicaciones, modificaciones de equipos docentes, o impersonación. El audit-log es un requerimiento transversal: todos los módulos del dominio (C-07 a C-20) registrarán acciones aquí. C-04 ya definió el permiso `auditoria:ver` y la constante `impersonacion:usar`.

## Goals / Non-Goals

**Goals:**
- Modelar `AuditLog` como tabla append-only en PostgreSQL, con restricción a nivel DB (trigger BEFORE UPDATE/DELETE) y a nivel app (repositorio sin update/delete)
- Implementar `AuditService` que permita a cualquier servicio del dominio registrar acciones con código estandarizado, detalle JSON, IP, user-agent, filas afectadas
- Soportar impersonación: la sesión distingue actor real vs impersonado, el audit log registra ambos
- Contar los códigos de acción del catálogo como constantes en `permisos.py`
- Migración 0014 con la tabla `audit_log`
- Endpoint de consulta del audit log con filtros, protegido por `auditoria:ver`
- Tests: append-only, impersonación, códigos de acción, consulta con filtros

**Non-Goals:**
- Retención/purgado de registros (sin límite por ahora)
- Notificaciones/reacciones en tiempo real a eventos de auditoría
- Integración con sistemas externos de SIEM
- UI de visualización de auditoría (corresponde a C-21 frontend)

## Decisions

### D1: Append-only enforcement con dos capas
El audit-log se protege en dos niveles:
1. **App layer**: el repositorio `AuditLogRepository` solo expone `create()` y `list()`. No hay métodos `update()` ni `delete()`. Los servicios nunca reciben referencia para modificar entradas.
2. **DB layer**: trigger `BEFORE UPDATE` y `BEFORE DELETE` en la tabla `audit_log` que lanzan excepción. Esto cubre el caso de acceso directo a DB (consola SQL, scripts, migraciones maliciosas).

Alternativa considerada: solo app layer. Rechazada: un operador con acceso directo a DB podría modificar registros sin pasar por la app. La doble capa es defense-in-depth.

### D2: AuditService como servicio central, no decorator
Se implementa `AuditService(db, current_user, request)` con un método `log(accion, detalle, filas_afectadas, materia_id=None)`. Lee `actor_id` e `impersonado_id` del `CurrentUser`, y `ip`/`user_agent` del request object.

Los servicios del dominio llaman a `audit_service.log(...)` después de completar la acción. Para conveniencia, se proveen helpers tipados como `log_calificaciones_importar(total_filas)` que fijan el código automáticamente.

Alternativa considerada: decorator `@audit(accion="CALIFICACIONES_IMPORTAR")` sobre métodos de servicio. Rechazada: los decoradores no tienen acceso fácil al contexto específico (detalle JSON, filas_afectadas) que varía por llamada. El service explícito es más flexible y testeable.

Alternativa considerada: eventos asíncronos (pub/sub). Rechazada: el audit log debe ser síncrono — si el registro falla, la acción debe poder revertirse. Además agrega complejidad innecesaria para un MVP.

### D3: Impersonación detectable desde CurrentUser
El `CurrentUser` (definido en `AuthService`) se extiende con un campo opcional `impersonator_id: UUID | None`:
- `None` → sesión normal
- `UUID` → sesión bajo impersonación, donde `impersonator_id` es el usuario real que inició la impersonación y `user_id` es el usuario impersonado

Cuando `impersonator_id` no es `None`, `AuditService` usa ese valor como `actor_id` y `user_id` como `impersonado_id`. Esto garantiza que las acciones queden atribuidas al actor real.

El guard `require_permission` evalúa permisos del usuario impersonado (roles del CurrentUser), no del impersonator. El permiso `impersonacion:usar` se verifica al iniciar la impersonación.

Alternativa considerada: almacenar impersonator_id en un header/contexto separado. Rechazada: viola el principio de que la identidad SIEMPRE viene de la sesión JWT (Regla Dura #8).

### D4: Migración 0014 como fecha actual + secuencia
La migración sigue el patrón existente: `20260607_0014_audit_log.py`, con revision id `20260607_0014`, dependiente de la última migración `20260607_0013`.

Incluye:
- CREATE TABLE `audit_log`
- CREATE OR REPLACE FUNCTION `reject_audit_log_modification()` (trigger function)
- CREATE TRIGGER `audit_log_append_only_before_update` BEFORE UPDATE ON `audit_log`
- CREATE TRIGGER `audit_log_append_only_before_delete` BEFORE DELETE ON `audit_log`

Los triggers usan `RAISE EXCEPTION` para rechazar modificaciones.

### D5: Consulta de auditoría como endpoint separado
Se implementa `GET /api/v1/audit/logs` con filtros opcionales:
- `fecha_desde`, `fecha_hasta` (datetime)
- `actor_id` (UUID)
- `accion` (string)
- `materia_id` (UUID, opcional)
- Paginación estándar (limit/offset)

Protegido con `require_permission("auditoria:ver")`. Siempre scoped por tenant del usuario autenticado (el repositorio filtra por `tenant_id`).

## Risks / Trade-offs

- [Riesgo] Los triggers BEFORE UPDATE/DELETE pueden ser omitidos si la migración se ejecuta parcialmente. Mitigación: la migración es atómica; si falla, se revierte completa.
- [Riesgo] El audit-log síncrono agrega latencia a las operaciones del dominio (~1-5ms por insert). Mitigación: aceptable para el volumen esperado; si escala, migrar a escritura batch asíncrona con tabla separada.
- [Trade-off] Sin purga de datos, la tabla `audit_log` crece indefinidamente. Esto es deliberado: la KB exige "sin límite de retención, sin posibilidad de edición ni borrado". Si el volumen lo requiere, se puede particionar por fecha.
- [Riesgo] El `AuditService` necesita acceso al request object (IP, user-agent). Esto lo acopla ligeramente a FastAPI. Mitigación: extraer IP/user-agent en el router/dependency y pasarlos como parámetros al servicio, manteniendo el servicio puro.
