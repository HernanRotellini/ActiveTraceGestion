## Why

El perfil COORDINADOR y ADMIN necesitan interfaces de gestión completas para administrar equipos docentes, avisos, tareas internas, encuentros, coloquios, monitores transversales y la configuración del cuatrimestre. Sin estas pantallas, la plataforma solo cubre el flujo del perfil PROFESOR (C-22) — el backend ya tiene las APIs (C-08, C-13, C-14, C-15, C-16, C-17) pero no hay forma de que coordinadores y administradores operen sobre ellas.

## What Changes

- **Features frontend para COORDINADOR/ADMIN** dentro de `frontend/src/features/`:
  - `equipos-docentes/`: CRUD completo, creación masiva, clonar desde cuatrimestre anterior, gestión de vigencia, export a CSV
  - `avisos/`: ABM con scope de destino (roles, comisiones, individual), acknowledgment tracking, historial
  - `tareas-internas/`: Workflow completo con comentarios, asignación, cambio de estado, filtros
  - `monitores/`: Dashboards transversales con métricas generales (F2.7, F2.9)
  - `encuentros/`: Administración de slots, instancias, guardias
  - `coloquios/`: Administración de evaluaciones, reservas, resultados
  - `setup-cuatrimestre/`: FL-03 — configuración del período académico (fechas, programas)
- **Nuevas rutas lazy-loaded** en el router principal, protegidas por `PermissionGuard` con permisos `modulo:accion`
- **Items de menú dinámico** para estos features en MainLayout, visibles solo para COORDINADOR/ADMIN
- Sin cambios en backend — solo frontend

## Capabilities

### New Capabilities
- `frontend-equipos-docentes`: UI para gestión CRUD de equipos docentes: listado, alta/edición individual y masiva, clonar entre períodos, modificar vigencia general, exportar a CSV
- `frontend-avisos`: UI para ABM de avisos con scope de destino (roles, comisiones, usuarios), acknowledgment tracking (quién vio, quién falta), historial
- `frontend-tareas-internas`: UI para workflow de tareas internas: creación, asignación, cambio de estado, comentarios encadenados, filtros por estado/asignado/prioridad
- `frontend-monitores`: Dashboards con métricas generales (F2.7 distribución de alumnos, F2.9 atrasos y entregas) con filtros por comisión/materia/período
- `frontend-encuentros`: UI para administración de encuentros: slots horarios, instancias de dictado, registro de guardias
- `frontend-coloquios`: UI para administración de evaluaciones de coloquio: reservas, resultados, gestión de instancias
- `frontend-setup-cuatrimestre`: UI para FL-03: configuración del período académico (fechas clave, programas por materia, vigencia)

### Modified Capabilities
- (ninguna — todos los specs existentes de frontend no requieren cambios de comportamiento)

## Impact

- `frontend/src/features/` — 7 nuevos feature modules
- `frontend/src/router/` — nuevas rutas lazy-loaded con guards
- `frontend/src/shared/components/` — posible necesidad de nuevos componentes compartidos (DataTable, WizardModal, KanbanBoard)
- `frontend/src/shared/layout/` — items de menú para COORDINADOR/ADMIN
- Sin cambios en backend, DB, schemas, ni modelos
