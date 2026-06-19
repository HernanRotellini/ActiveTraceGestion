# Checklist — Coloquios

> Fuentes: `knowledge-base/06_funcionalidades.md` (Épica 7, F7.1–F7.5), `backend/app/api/v1/routers/coloquios.py`, `backend/app/schemas/coloquio.py`, `backend/app/models/coloquio.py`

## Contratos de API (según backend)

- [x] `GET /api/coloquios/metricas` → `MetricasColoquiosResponse` (F7.1)
- [x] `POST /api/coloquios` → `EvaluacionResponse` con turnos (F7.3)
- [x] `GET /api/coloquios` → `EvaluacionListResponse[]` (filter: materia_id) (F7.4)
- [x] `GET /api/coloquios/{id}` → `EvaluacionResponse` con turnos
- [x] `POST /api/coloquios/{id}/importar-alumnos` → `{ importados: number }` (F7.2)
- [x] `GET /api/coloquios/{id}/turnos` → `TurnoResponse[]`
- [x] `GET /api/coloquios/{id}/reservas` → `ReservaResponse[]`
- [x] `POST /api/coloquios/{id}/resultados` → `ResultadoResponse`
- [x] `GET /api/coloquios/{id}/resultados` → `ResultadoResponse[]`
- [x] `DELETE /api/coloquios/{id}` → `{ mensaje: string }` (cerrar convocatoria)
- [x] `GET /api/coloquios/admin/agenda` → `{ items: AgendaReservaResponse[], total: number }`

## Tipos correctos

- [x] `EvaluacionListResponse`: id, materia_id, cohorte_id, tipo, instancia, estado, total_turnos, alumnos_convocados, reservas_activas, cupos_libres, created_at
- [x] `EvaluacionResponse`: id, materia_id, cohorte_id, tipo, instancia, estado, turnos[], created_at, updated_at
- [x] `TurnoResponse`: id, evaluacion_id, fecha, hora_inicio?, hora_fin?, cupo_maximo, cupo_restante
- [x] `ReservaResponse`: id, evaluacion_id, turno_id, alumno_id, estado, created_at
- [x] `ResultadoCreate`: alumno_id, nota_final (string, ej: "7" o "Ausente")
- [x] `ResultadoResponse`: id, evaluacion_id, alumno_id, nota_final, registrado_por, created_at, updated_at
- [x] Eliminados: `comision_id`, `comision_nombre`, `aula`, `observaciones`, `fecha` (no existen en convocatoria)
- [x] Eliminada: `ResultadoColoquio` (pendiente/aprobado/desaprobado/ausente) — backend usa `nota_final: str` libre
- [x] Eliminada: campo `confirmado` de Reserva (backend usa `estado: str`)

## Servicios

- [x] URL base `/api/coloquios` (con `/api/` prefix)
- [x] `panelMetricas()` → GET /api/coloquios/metricas
- [x] `listarConvocatorias(filters?)` → GET /api/coloquios
- [x] `obtenerConvocatoria(id)` → GET /api/coloquios/{id}
- [x] `crearConvocatoria(payload)` → POST /api/coloquios
- [x] `cerrarConvocatoria(id)` → DELETE /api/coloquios/{id}
- [x] `importarAlumnos(id, alumno_ids[])` → POST /api/coloquios/{id}/importar-alumnos
- [x] `listarReservas(id)` → GET /api/coloquios/{id}/reservas
- [x] `registrarResultado(id, payload)` → POST /api/coloquios/{id}/resultados
- [x] `listarResultados(id)` → GET /api/coloquios/{id}/resultados
- [x] Eliminados: `confirmarReserva`, `cancelarReserva` (no existen en backend)
- [x] Eliminada: `actualizarColoquio` (no hay PATCH para convocatoria)

## Hooks

- [x] `useMetricasColoquios()` — query key `['coloquios-metricas']`
- [x] `useColoquiosList(filters?)` — query key `['coloquios', filters]`, retorna `EvaluacionListResponse[]`
- [x] `useColoquio(id)` — query key `['coloquio', id]`, retorna `EvaluacionResponse` (con turnos)
- [x] `useReservas(evaluacionId)` — query key `['coloquio-reservas', id]`
- [x] `useResultados(evaluacionId)` — query key `['coloquio-resultados', id]`
- [x] `useCrearConvocatoria()` — invalida lista + métricas
- [x] `useCerrarConvocatoria()` — invalida lista + métricas
- [x] `useImportarAlumnos(evaluacionId)` — invalida detalle
- [x] `useRegistrarResultado(evaluacionId)` — invalida resultados + métricas
- [x] Eliminados: `useActualizarColoquio`, `useConfirmarReserva`, `useCancelarReserva`

## ColoquiosListPage (F7.4/F7.1)

- [x] Panel de métricas en la parte superior (4 tarjetas: convocatorias_activas, alumnos_convocados, reservas_activas, notas_registradas) — F7.1
- [x] Filtro solo por materia_id (único filtro disponible en el backend)
- [x] Columnas: tipo, instancia, estado, total_turnos, alumnos_convocados, reservas_activas, cupos_libres, created_at
- [x] Link "Nueva Convocatoria"
- [x] Link "Ver" por fila → detalle
- [x] Toast de error de carga

## ColoquioDetailPage (F7.3/F7.5)

- [x] Muestra: instancia (título), tipo, estado, created_at
- [x] Botón "Cerrar convocatoria" (DELETE) cuando estado no es cerrado, con confirmación
- [x] Tabla de turnos: fecha, hora_inicio, hora_fin, cupo_maximo, cupo_restante
- [x] Tabla de reservas: alumno_id, turno_id, estado, created_at (UUIDs — sin nombre resuelto)
- [x] Tabla de resultados + botón "Registrar nota" con form (alumno_id + nota_final libre)
- [x] Toast éxito/error en todas las acciones

## Criterios transversales

- [x] Identidad desde JWT (no URL/body)
- [x] Multi-tenancy: backend filtra por tenant
- [x] RBAC: `coloquios:ver` / `coloquios:gestionar` / `coloquios:reservar`
- [x] Soft delete: cerrar = DELETE (el backend lo maneja como soft delete)
- [x] Auditoría: acciones auditadas por el backend
- [x] Sin `any` en TypeScript
