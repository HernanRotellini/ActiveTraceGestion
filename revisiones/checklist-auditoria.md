# Checklist — Auditoría

> Fuentes: `backend/app/api/v1/routers/audit.py`, `backend/app/api/v1/routers/auditoria.py`, `backend/app/schemas/audit.py`, `backend/app/schemas/panel_auditoria.py`

## Contratos de API (según backend)

### Panel de auditoría (`/api/v1/auditoria/panel/`)
- [x] `GET /api/v1/auditoria/panel/acciones-por-dia` → `{ items: AccionesPorDia[] }` (filtros: fecha_desde, fecha_hasta, materia_id)
- [x] `GET /api/v1/auditoria/panel/comunicaciones-por-docente` → `{ items: ComunicacionPorDocente[] }` (filtros: fecha_desde, fecha_hasta, materia_id)
- [x] `GET /api/v1/auditoria/panel/interacciones-por-docente-materia` → `{ items: Interaccion[] }` (filtros: fecha_desde, fecha_hasta, actor_id)
- [x] `GET /api/v1/auditoria/panel/ultimas-acciones` → `{ items: UltimaAccion[] }` (params: max_results, offset)

### Log de auditoría (`/api/v1/audit/`)
- [x] `GET /api/v1/audit/logs` → `{ items: AuditoriaEntry[], total: number }` (filtros: fecha_desde, fecha_hasta, actor_id, accion, materia_id, limit, offset)

## Tipos correctos

### AuditoriaEntry (AuditLogResponse del backend)
- [x] Campos correctos: id, tenant_id, fecha_hora, actor_id, impersonado_id?, materia_id?, accion, detalle (Record), filas_afectadas?, ip?, user_agent?
- [x] Eliminado campos incorrectos: usuario, materia, registros_afectados, ip_origen (no existen en backend)

### Panel types
- [x] `AccionesPorDia`: fecha (string), total (number)
- [x] `ComunicacionPorDocente`: docente_id, accion, total — SIN docente_nombre, enviadas, pendientes, fallidas
- [x] `Interaccion`: docente_id, materia_id?, accion, total — SIN docente_nombre, materia (string)
- [x] `UltimaAccion`: mismos campos que AuditoriaEntry

### AuditoriaFilters
- [x] Filtros correctos: fecha_desde?, fecha_hasta?, actor_id?, accion?, materia_id?, limit?, offset?
- [x] Eliminado: usuario (string), materia (string), page — backend toma actor_id (UUID) y materia_id (UUID)

### MetricasDashboard
- [x] Eliminado — no existe endpoint `/panel-auditoria/metricas` en el backend

## Servicio

- [x] `listarLogAuditoria` → `/api/v1/audit/logs` (era `/audit-trail`)
- [x] `listarAccionesPorDia` → `/api/v1/auditoria/panel/acciones-por-dia`
- [x] `listarComunicacionesPorDocente` → `/api/v1/auditoria/panel/comunicaciones-por-docente`
- [x] `listarInteracciones` → `/api/v1/auditoria/panel/interacciones-por-docente-materia`
- [x] `listarUltimasAcciones` → `/api/v1/auditoria/panel/ultimas-acciones`
- [x] Eliminado `obtenerMetricas` (URL `/panel-auditoria/metricas` no existe)

## Hooks

- [x] `useLogAuditoria` actualizado con filtros correctos (limit/offset en vez de page/limit)
- [x] `useAccionesPorDia`, `useComunicacionesPorDocente`, `useInteracciones`, `useUltimasAcciones`
- [x] Eliminado `useMetricas` (endpoint no existe)

## Páginas

### AuditoriaDashboardPage
- [x] Usa 4 hooks separados en vez de useMetricas
- [x] `comunicaciones` muestra docente_id + accion + total (sin docente_nombre, sin enviadas/pendientes/fallidas)
- [x] `interacciones` muestra docente_id + materia_id + accion + total (sin nombres)
- [x] "Últimas acciones" usa `useUltimasAcciones` (endpoint dedicado)
- [x] Filtros solo con campos que el backend acepta (fecha_desde, fecha_hasta, accion)

### AuditoriaLogPage
- [x] Tabla muestra actor_id, accion, filas_afectadas, ip, user_agent (no usuario/materia strings)
- [x] Paginación usa limit/offset (no page/limit)
- [x] Filtros: accion (string), fecha_desde, fecha_hasta (sin usuario texto ni materia texto)

### AuditoriaFiltros
- [x] Removido filtro `usuario` (texto — backend acepta UUID, no string)
- [x] Removido filtro `materia` (texto — backend acepta UUID, no string)
- [x] Mantiene: accion, fechaDesde, fechaHasta

## Tests

- [x] `Auditoria.test.tsx` actualizado para coincidir con props correctas de `AuditoriaFiltros`

## Criterios transversales

- [x] URLs `/api/v1/` prefix correcto
- [x] Identidad desde JWT
- [x] RBAC: `auditoria:ver`
- [x] Sin `any` en TypeScript
