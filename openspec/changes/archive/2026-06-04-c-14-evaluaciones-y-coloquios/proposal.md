## Why

Activia Trace necesita soportar el ciclo completo de evaluaciones orales (coloquios): desde la creación de la convocatoria por parte de coordinación, la importación de alumnos habilitados, la reserva de turnos por parte de los alumnos, hasta el registro de resultados. Sin este módulo, el proceso de evaluación final queda fuera del sistema, rompiendo la trazabilidad que exige el producto (todo audita). C-07 (usuarios-y-asignaciones) ya proveyó la base de usuarios y asignaciones sobre la que este módulo se apoya.

## What Changes

- Nuevos modelos: `Evaluacion`, `ReservaEvaluacion`, `ResultadoEvaluacion`
- Creación de convocatoria de coloquio (F7.3): materia, instancia, días con cupos
- Importación de alumnos a una convocatoria (F7.2)
- Listado de convocatorias con métricas operativas (F7.4)
- Panel de métricas global (F7.1): total alumnos cargados, instancias activas, reservas activas, notas registradas
- Admin global de coloquios (F7.5): gestión de convocatorias, registro consolidado de resultados, agenda de reservas
- Reserva de turno por ALUMNO: selecciona día disponible con cupo, estado Activa/Cancelada
- `TurnoEvaluacion` como entidad separada (día + cupo máximo + cupos restantes), vinculada a `Evaluacion`
- RBAC: nuevos permisos `coloquios:gestionar` (COORDINADOR/ADMIN) y `coloquios:reservar` (ALUMNO)
- Endpoints `/api/coloquios/*` con guards de permiso según operación
- Migración Alembic: tablas `evaluacion`, `turno_evaluacion`, `reserva_evaluacion`, `resultado_evaluacion`
- Tests: creación de turnos con cupo, reserva resta cupo, rechazo sin cupo, métricas consolidadas

## Capabilities

### New Capabilities
- `coloquios-gestion`: Gestión completa de coloquios — CRUD de convocatorias, importación de alumnos, listado con métricas, panel de métricas global, admin global con registro de resultados. Accesible por COORDINADOR/ADMIN vía permiso `coloquios:gestionar`.
- `coloquios-reserva`: Reserva y cancelación de turnos de coloquio por parte de ALUMNO. Validación de cupo disponible, control de estado Activa/Cancelada, impedimento de reserva duplicada o sin cupo. Accesible por ALUMNO vía permiso `coloquios:reservar`.

### Modified Capabilities
- Ninguna — este change introduce capacidades completamente nuevas sin modificar specs existentes.

## Impact

- **Backend**: Nuevos archivos en `backend/app/models/`, `backend/app/repositories/`, `backend/app/services/`, `backend/app/schemas/`, `backend/app/api/v1/routers/`.
- **Base de datos**: 4 tablas nuevas (`evaluacion`, `turno_evaluacion`, `reserva_evaluacion`, `resultado_evaluacion`). Migración Alembic.
- **RBAC**: Seed de permisos actualizado con `coloquios:gestionar` y `coloquios:reservar`.
- **Dependencias**: C-07 ya completado (usuarios, asignaciones, Materia). No hay dependencias nuevas.
- **Sin impacto en seguridad**: no se maneja PII, no se requiere cifrado adicional.
