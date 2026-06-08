## Why

C-24 es el último change frontend del proyecto. Cierra la capa de presentación para los módulos de FINANZAS y ADMIN, que ya tienen backend completo (C-18 liquidaciones-y-honorarios y C-19 panel-auditoria-metricas). Sin estas vistas, los roles FINANZAS y ADMIN no pueden operar ni auditar el sistema.

## What Changes

- **Feature FINANZAS**: nuevo módulo `liquidaciones` con vista del período (segmentada general/NEXO/factura + KPIs), cierre de liquidación, historial de liquidaciones cerradas, grilla salarial (ABM salarios base y plus con vigencia), gestión de facturas de docentes.
- **Feature ADMIN**: nuevo módulo `admin` con estructura académica (CRUD carreras, cohortes, materias), usuarios del tenant (CRUD con PII cifrada + búsqueda), panel de auditoría y métricas (consumiendo backend C-19), log completo de auditoría.
- **Routing**: nuevas rutas protegidas en `/admin/*` y `/liquidaciones/*`.
- **Menú dinámico**: ítems visibles según permisos `liquidaciones:*`, `estructura:*`, `usuarios:*`, `auditoria:*`.

## Capabilities

### New Capabilities
- `frontend-liquidaciones`: Vista de liquidaciones del período con segmentación contable (general / NEXO / factura), KPIs de cabecera, cierre, historial.
- `frontend-admin-estructura`: CRUD de carreras, cohortes y materias con filtros y paginación.
- `frontend-admin-usuarios`: CRUD de usuarios del tenant con PII cifrada, filtros y asignación de roles.
- `frontend-admin-auditoria`: Panel de auditoría con métricas de uso, gráficos y log completo con filtros.

### Modified Capabilities
- `frontend-shell`: Nuevas rutas `/admin/*` y `/liquidaciones/*` en el router; nuevos ítems en el menú lateral.
- `frontend-route-guard`: Nuevos permisos requeridos (`liquidaciones:ver`, `liquidaciones:configurar-salarios`, `estructura:gestionar`, `usuarios:gestionar`, `auditoria:ver`).

## Impact

- `frontend/src/features/liquidaciones/` — módulo nuevo (~25 archivos)
- `frontend/src/features/admin/` — módulo nuevo (~30 archivos)
- `frontend/src/routes/index.tsx` — nuevas rutas lazy
- `frontend/src/layouts/MainLayout.tsx` — nuevos ítems de menú
- `frontend/src/test/` — tests de componentes e integración
