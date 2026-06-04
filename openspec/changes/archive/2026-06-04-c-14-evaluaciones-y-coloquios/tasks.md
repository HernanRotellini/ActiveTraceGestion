## 1. Modelos

- [x] 1.1 Crear `backend/app/models/coloquio.py` con modelos: `Evaluacion` (enum TipoEvaluacion, enum EstadoEvaluacion), `TurnoEvaluacion`, `ReservaEvaluacion` (enum EstadoReserva), `ResultadoEvaluacion`, `ConvocatoriaAlumno`
- [x] 1.2 Actualizar `backend/app/models/__init__.py` para exportar los nuevos modelos

## 2. Migración

- [x] 2.1 Generar migración Alembic `0NN_evaluaciones_y_coloquios` con tablas: `evaluacion`, `turno_evaluacion`, `reserva_evaluacion`, `resultado_evaluacion`, `convocatoria_alumno`
- [x] 2.2 Verificar que la migración incluye índices, unique constraints, y foreign keys correctas (tenant_id, materia_id, cohorte_id, etc.)

## 3. Schemas Pydantic

- [x] 3.1 Crear `backend/app/schemas/coloquio.py` con schemas request/response para cada endpoint, usando `extra='forbid'`
- [x] 3.2 Incluir schemas: `EvaluacionCreate`, `EvaluacionResponse`, `TurnoResponse`, `ReservaResponse`, `ResultadoCreate`, `ResultadoResponse`, `MetricasResponse`, `ImportarAlumnosRequest`

## 4. Repositorio

- [x] 4.1 Crear `backend/app/repositories/coloquio_repository.py` con `ColoquioRepository(TenantScopedRepository[Evaluacion])` y métodos para CRUD de evaluaciones, turnos, reservas (con UPDATE atómico de cupo), importación de alumnos, métricas globales

## 5. Servicio

- [x] 5.1 Crear `backend/app/services/coloquio_service.py` con `ColoquioService` orquestando: crear convocatoria (crea evaluacion + turnos), importar alumnos, listar con métricas, panel de métricas global, reservar (valida cupo + permiso + transacción atómica), cancelar reserva (restituye cupo), registrar/actualizar resultados, admin global (agenda de reservas, resultados consolidados)
- [x] 5.2 Incluir registro de auditoría en acciones: crear convocatoria, importar alumnos, reservar, cancelar, registrar resultado, cerrar convocatoria

## 6. Router y permisos

- [x] 6.1 Crear `backend/app/api/v1/routers/coloquios.py` con endpoints listados en diseño D4, usando guards `require_permission(COLOQUIOS_GESTIONAR)` y `require_permission(COLOQUIOS_RESERVAR)`
- [x] 6.2 Agregar constantes `COLOQUIOS_GESTIONAR` y `COLOQUIOS_RESERVAR` en `backend/app/models/permisos.py`
- [x] 6.3 Actualizar seed de RBAC para incluir `coloquios:gestionar` en roles COORDINADOR y ADMIN, y `coloquios:reservar` en rol ALUMNO
- [x] 6.4 Registrar el router en `backend/app/api/v1/__init__.py`

## 7. Tests

- [x] 7.1 Escribir tests de unidad/servicio: creación de convocatoria con turnos, importación de alumnos, reserva con cupo (resta cupo), reserva sin cupo (rechaza), cancelación (restituye cupo), reserva duplicada (rechaza), alumno no convocado (rechaza)
- [x] 7.2 Escribir tests de métricas: panel global (convocados/reservas/notas), listado con métricas por convocatoria
- [x] 7.3 Escribir tests de permisos: 403 en endpoints de gestión sin permiso, 403 en endpoint de reserva sin permiso ALUMNO
- [x] 7.4 Verificar cobertura ≥80% líneas, ≥90% reglas de negocio
