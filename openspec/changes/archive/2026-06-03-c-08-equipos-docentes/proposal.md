## Why

El modelo de Asignacion (C-07) ya provee CRUD individual. Sin embargo, los flujos reales de gestión de equipos docentes requieren operaciones de alto nivel: el COORDINADOR necesita asignar varios docentes en bloque al inicio del cuatrimestre (F4.4), clonar equipos del período anterior (F4.5, RN-12), modificar vigencias de todo un equipo de una sola vez (F4.6), y exportar la composición del equipo (F4.7). Además, cada docente necesita una vista de "mis equipos" que muestre sus propias asignaciones (F4.2). C-08 agrega estas operaciones como una capa de servicios de orquestación sobre el modelo de Asignacion existente.

## What Changes

- **Nuevo router** `/api/equipos/*` con las operaciones de equipo (mis-equipos, asignación masiva, clonar, vigencia, exportar)
- **Servicio `EquipoService`** que orquesta operaciones bulk sobre `AsignacionRepository` (asignación masiva, clonado con RN-12, modificación de vigencia en bloque)
- **Vista `mis-equipos`** accesible por cualquier rol docente autenticado (PROFESOR, TUTOR, NEXO, COORDINADOR) — muestra sus asignaciones con filtros
- **Exportación** de equipo a CSV
- **Placeholder de auditoría** (`ASIGNACION_MODIFICAR`) inline, reemplazable por C-05 cuando esté disponible
- No se modifican modelos existentes (Asignacion, Usuario) — solo se agregan servicios y endpoints

## Capabilities

### New Capabilities
- `equipos-docentes`: Gestión de equipos docentes con operaciones de alto nivel (mis-equipos, asignación masiva, clonado entre períodos, modificación de vigencia general, exportación)

### Modified Capabilities
- Ninguna — las reglas de Asignacion no cambian a nivel spec

## Impact

- **Nuevo archivo**: `backend/app/services/equipos.py` — EquipoService con lógica bulk y clonado
- **Nuevo archivo**: `backend/app/api/v1/routers/equipos.py` — router con endpoints de equipo
- **Nuevo archivo**: `backend/app/schemas/equipos.py` — DTOs para operaciones bulk
- **Modificación**: `backend/app/main.py` — wire del nuevo router
- **Tests**: `backend/tests/test_equipos.py` — tests para todas las operaciones bulk
- **Sin nuevos modelos**: reusa `AsignacionRepository` y `AsignacionService` existentes
- **Sin migración**: no hay cambios de esquema
