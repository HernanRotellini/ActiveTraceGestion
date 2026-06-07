## Why

La coordinación académica necesita un flujo interno trazable para asignar, delegar y cerrar tareas entre docentes sin depender de canales externos. Este change implementa C-16 para dar soporte backend al workflow de tareas internas de alto uso, manteniendo aislamiento multi-tenant, RBAC fino e historial de comentarios.

## What Changes

- Agrega la capacidad de crear tareas internas asociadas opcionalmente a una materia o contexto de dominio.
- Permite consultar “mis tareas” para el usuario autenticado y una vista global filtrable para coordinación/administración.
- Permite delegar/reasignar tareas conservando trazabilidad de `asignado_por` y `asignado_a`.
- Define el workflow de estados `Pendiente → En progreso → Resuelta` y `Pendiente/En progreso → Cancelada`, con comentarios en hilo.
- Expone endpoints `/api/tareas/*` protegidos por `tareas:gestionar` y siempre acotados al tenant de la sesión.
- Agrega persistencia para `Tarea` y `ComentarioTarea` mediante una migración Alembic dedicada.

## Capabilities

### New Capabilities
- `tareas-internas`: Gestión de tareas internas, delegación, comentarios y workflow de estado para coordinación y equipos docentes.

### Modified Capabilities

No se modifican requisitos de capacidades existentes.

## Impact

- Backend: nuevos modelos, schemas, repositories, services y router para tareas internas.
- Base de datos: nueva migración para tablas `tarea` y `comentario_tarea`, con `tenant_id`, soft delete, índices de consulta y FKs a usuarios/materias.
- Seguridad: endpoints con JWT, identidad desde sesión, permisos `tareas:gestionar` y scope row-level por tenant.
- Tests: cobertura TDD para alta/asignación, delegación, transiciones, comentarios, filtros y aislamiento multi-tenant.
