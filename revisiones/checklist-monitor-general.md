# Checklist — Monitor General

> Fuentes: `knowledge-base/06_funcionalidades.md`, `backend/app/api/v1/routers/analisis.py`, `backend/app/schemas/analisis.py`

## Contratos de API (según backend)

- [x] `GET /api/analisis/monitor` → `MonitorResponse { items: MonitorItem[], total: number }` con filtros opcionales

## Filtros disponibles (según backend query params)

- [x] `materia_id` (UUID)
- [x] `busqueda` (str)
- [x] `regional` (str)
- [x] `comision` (str)
- [x] `actividad` (str)
- [x] `min_actividad_cumplida` (int)
- [x] `page` (int, default 1)
- [x] `per_page` (int, default 50, max 200)
- [x] Eliminado `periodo` (no existe en el backend)

## Tipos correctos

- [x] `MonitorItem`: entrada_padron_id, alumno_nombre, email, regional?, comision?, total_actividades, aprobadas, pendientes, atrasado
- [x] `MonitorResponse`: items, total
- [x] Eliminado `periodo` de `MonitorFilters`

## MonitorGeneralPage (antes zombie — sin API)

- [x] Usa `useMonitor` con filtro `per_page: 200` (vista admin completa)
- [x] Métricas en tiempo real derivadas de los datos: total, al_día, atrasados, % atraso
- [x] Panel de filtros (MonitorFilters component) con todos los filtros reales
- [x] Tabla (MonitorTable component) con todos los alumnos
- [x] Toast de error de carga
- [x] Spinner mientras carga

## MonitorPage (ya correcto)

- [x] Usa `useMonitor` hook correctamente
- [x] Usa MonitorFilters y MonitorTable components
- [x] Toast de error
- [x] Spinner mientras carga

## Criterios transversales

- [x] URL `/api/analisis/monitor` (tiene `/api/` prefix)
- [x] Identidad desde JWT
- [x] RBAC: `atrasados:ver` (declarado en backend)
- [x] Sin `any` en TypeScript
