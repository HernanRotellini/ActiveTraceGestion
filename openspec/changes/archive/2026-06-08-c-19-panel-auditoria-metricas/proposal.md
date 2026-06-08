## Why

Actualmente el sistema registra todas las acciones significativas en el AuditLog (C-05) y expone un endpoint básico de listado con filtros. Sin embargo, los supervisores (COORDINADOR, ADMIN) y FINANZAS no tienen visibilidad agregada del uso del sistema: no pueden ver volumen de actividad por día, estado de comunicaciones por docente, métricas de interacción por docente×materia, ni un panel de últimas acciones con límite configurable. Sin estas vistas, es imposible detectar docentes inactivos, problemas operativos o realizar auditoría regulatoria eficiente.

## What Changes

- Nuevos endpoints de **panel de métricas** (`/api/v1/auditoria/panel/*`) de solo lectura sobre AuditLog:
  - Acciones por día (serie temporal para gráfico de volumen)
  - Estado de comunicaciones agrupado por docente
  - Interacciones por docente y materia
  - Últimas acciones con límite configurable (default 200)
- Endpoint de **log completo de auditoría** con filtros mejorados (hereda del existente `GET /api/v1/audit/logs`)
- Scope `(propio)` para COORDINADOR: solo ve acciones de los docentes de sus materias asignadas
- Tests completos de agregaciones, filtros, scope `(propio)`, límite configurable
- No se crean nuevos modelos de datos ni migraciones — todo es consulta sobre AuditLog existente

## Capabilities

### New Capabilities
- `panel-auditoria-metricas`: Panel de interacciones con agregaciones (acciones/día, comunicaciones por docente, interacciones por docente×materia, últimas acciones)

### Modified Capabilities
- `audit-log`: Se agrega scope `(propio)` para COORDINADOR y endpoint de log completo con paginación y filtros

## Impact

- **API**: Nuevo router `backend/app/api/v1/routers/auditoria.py` con prefijo `/api/v1/auditoria`
- **Services**: Nuevo `backend/app/services/panel_auditoria.py` con lógica de agregaciones y scope
- **Repositories**: Nuevo `backend/app/repositories/panel_auditoria.py` con queries de agregación SQL
- **Tests**: Nuevo `backend/tests/test_c19_panel_auditoria.py`
- **Permisos**: Reusa `auditoria:ver` existente; sin cambios en modelo de permisos
- **Dependencias**: Solo lectura sobre `AuditLog` (C-05) y `Asignacion` (C-07) para scope `(propio)`
