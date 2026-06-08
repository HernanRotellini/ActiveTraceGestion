## 1. Routes & Menu Setup

- [x] 1.1 Add new lazy imports in `routes/index.tsx` for all 7 coordinacion feature pages
- [x] 1.2 Add route definitions under `/coordinacion/*` with `PermissionGuard` wrappers
- [x] 1.3 Add route for `/monitores/general` (extension of existing module)
- [x] 1.4 Add menu items in `MainLayout.tsx` for coordinacion features with correct permission keys

## 2. Feature: equipos-docentes

- [x] 2.1 Create `features/equipos-docentes/{components,hooks,services,types,pages}` structure
- [x] 2.2 Define types (`EquipoDocente`, `Asignacion`, `AsignacionMasivaPayload`, `ClonePayload`, `VigenciaPayload`) in `types/`
- [x] 2.3 Create `services/api.ts` with TanStack Query hooks for GET list, GET detail, POST create/masiva/clonar, PATCH vigencia, DELETE, GET export
- [x] 2.4 Implement `EquiposListPage` with paginated table, filters (materia, carrera, estado)
- [x] 2.5 Implement `EquipoDetailPage` with asignaciones table, vigencia management, export button
- [x] 2.6 Implement `EquipoFormPage` for individual creation/editing
- [x] 2.7 Implement modal/flujo de asignación masiva con selector de usuarios
- [x] 2.8 Implement modal de clonar equipo (origen → destino con selector de período)
- [x] 2.9 Implement export CSV button component

## 3. Feature: avisos

- [x] 3.1 Create `features/avisos/{components,hooks,services,types,pages}` structure
- [x] 3.2 Define types (`Aviso`, `AvisoScope`, `AckStatus`) in `types/`
- [x] 3.3 Create `services/api.ts` with TanStack Query hooks for CRUD avisos, publish, ack tracking
- [x] 3.4 Implement `AvisosListPage` with paginated table, filters (estado, fecha)
- [x] 3.5 Implement `AvisoFormPage` with scope selector (por rol, por comisión, por usuario)
- [x] 3.6 Implement `AvisoDetailPage` with content view, publish button, ack tracking table
- [x] 3.7 Implement componente `AckProgressBar` con stats (leídos/pendientes/total)

## 4. Feature: tareas-internas

- [x] 4.1 Create `features/tareas-internas/{components,hooks,services,types,pages}` structure
- [x] 4.2 Define types (`Tarea`, `Comentario`, `TareaEstado`, `Prioridad`) in `types/`
- [x] 4.3 Create `services/api.ts` with TanStack Query hooks for CRUD tareas, change estado, comentarios
- [x] 4.4 Implement `TareasListPage` with paginated table, filters (estado, asignado, prioridad, fecha)
- [x] 4.5 Implement `TareaDetailPage` with full detail, estado transitions, timeline de actividad
- [x] 4.6 Implement component `ComentarioList` for threaded comments with form
- [x] 4.7 Implement `TareaFormPage` for creation with asignación, prioridad, fecha límite

## 5. Feature: monitores (extensión)

- [x] 5.1 Create `features/monitores/pages/MonitorGeneralPage.tsx` (new page in existing module)
- [x] 5.2 Implement cards de métricas generales (total alumnos, distribución por comisión)
- [x] 5.3 Implement dashboard de atrasos y entregas (F2.9): métricas, tabla por materia
- [x] 5.4 Implement filtros compartidos (materia, período) y botón de export CSV

## 6. Feature: encuentros

- [x] 6.1 Create `features/encuentros/{components,hooks,services,types,pages}` structure
- [x] 6.2 Define types (`Encuentro`, `SlotHorario`, `InstanciaDictado`, `Guardia`) in `types/`
- [x] 6.3 Create `services/api.ts` with TanStack Query hooks for CRUD encuentros, slots, instancias, guardias
- [x] 6.4 Implement `EncuentrosListPage` with paginated table, filters (fecha, materia)
- [x] 6.5 Implement `EncuentroDetailPage` with slots, instancias, guardias management

## 7. Feature: coloquios

- [x] 7.1 Create `features/coloquios/{components,hooks,services,types,pages}` structure
- [x] 7.2 Define types (`EvaluacionColoquio`, `Reserva`, `Resultado`) in `types/`
- [x] 7.3 Create `services/api.ts` with TanStack Query hooks for CRUD evaluaciones, reservas, resultados
- [x] 7.4 Implement `ColoquiosListPage` with paginated table, filters (materia, estado)
- [x] 7.5 Implement `ColoquioDetailPage` with reservas list, confirm/cancel, carga de resultados

## 8. Feature: setup-cuatrimestre

- [x] 8.1 Create `features/setup-cuatrimestre/{components,hooks,services,types,pages}` structure
- [x] 8.2 Define types (`PeriodoAcademico`, `FechaAcademica`, `ProgramaMateria`) in `types/`
- [x] 8.3 Create `services/api.ts` with TanStack Query hooks for fechas académicas, programas, activación
- [x] 8.4 Implement `SetupCuatrimestrePage` with fecha keys management and program assignment
- [x] 8.5 Implement activation/deactivation flow with validation

## 9. Tests

- [x] 9.1 Write tests for equipos-docentes pages (listado, creación, clonado)
- [x] 9.2 Write tests for avisos pages (ABM, publicación, ack tracking)
- [x] 9.3 Write tests for tareas-internas (workflow de estados, comentarios)
- [x] 9.4 Write tests for monitores general (métricas, filtros, export)
- [x] 9.5 Write tests for encuentros, coloquios, setup-cuatrimestre pages
