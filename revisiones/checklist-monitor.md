# Checklist - Pantalla Monitor

## Fuentes revisadas

- `docs/SRS.md`: `/docente/monitor` requiere `atrasados:ver`; muestra alumnos de materias asignadas, actividad, aprobadas, pendientes; acciones: filtrar por alumno, comisión, regional, actividad.
- `knowledge-base/06_funcionalidades.md`: F2.8 — Monitor de seguimiento de alumnos (vista tutor/profesor); F2.9 — Monitor de seguimiento (vista coordinación/admin, extiende F2.8 con rango de fechas). F2.7 — Monitor general (coordinador/admin, filtros: materia, regional, comisión, búsqueda libre, estado, criterio de clasificación, exportar).
- `knowledge-base/11_historias_de_usuario.md`: HU-09 filtrar monitor general por materia, regional, comisión, búsqueda libre y estado; la vista filtrada debe exportarse.
- `knowledge-base/05_reglas_de_negocio.md`: RN-23 (auditoria de acciones significativas).
- `knowledge-base/03_actores_y_roles.md`: TUTOR y PROFESOR acceden al monitor de sus propias materias/comisiones asignadas.
- `revisiones/criterios-transversales-ux-ui.md`
- Backend real: `frontend/src/features/monitores/services/monitores.ts` (GET `/monitor/alumnos`, GET `/monitor/alumnos/exportar`), `MonitorPage.tsx`, `MonitorTable.tsx`, `MonitorFilters.tsx`, `monitores.ts` (types).

## Alcance esperado

La pantalla `/docente/monitor` es el **monitor de seguimiento propio** del docente (F2.8). Muestra el estado de actividades de los alumnos asignados al usuario autenticado — solo sus materias/comisiones. Es distinta del Monitor General (`/coordinacion/monitores`, F2.7) que es transversal al tenant.

- [ ] Mostrar estado de actividades de los alumnos asignados al usuario autenticado (solo scope propio).
- [ ] Filtrar por alumno, comisión, regional y actividad según SRS y F2.8.
- [ ] Mostrar estado visual por alumno: al día / atrasado / crítico.
- [ ] Exportar la vista filtrada.
- [ ] Respetar scope por rol: solo alumnos de las materias/comisiones propias del usuario.
- [ ] Mostrar error con Toast si falla la carga.

## Permisos esperados

- [x] Frontend: la ruta `/docente/monitor` está protegida con `atrasados:ver` (`PermissionGuard`).
- [x] Frontend: el menú lateral muestra "Monitor" solo con `atrasados:ver`.
- [ ] Backend: `GET /api/monitor/alumnos` debe filtrar por las materias/comisiones asignadas al usuario autenticado (scope propio del docente). Verificar que no devuelva alumnos de otras materias ni otros tenants.
- [ ] Backend: identidad siempre desde el JWT verificado (`current_user`), nunca desde parámetros de URL o body.
- [ ] Backend: toda consulta filtra por `tenant_id`.

## Campos esperados en el listado

- [x] `alumno_nombre` — nombre del alumno (legible, no UUID).
- [x] `comision` — comisión del alumno.
- [x] `materia` — nombre de la materia (legible, no UUID).
- [x] `actividades_pendientes` — cantidad de actividades pendientes.
- [x] `entregas_sin_corregir` — cantidad de entregas sin corregir.
- [x] `promedio_actual` — promedio actual (formateado a 2 decimales o `-` si es null).
- [x] `asistencias` — porcentaje de asistencia.
- [x] `estado` — badge visual: `Al día` / `Atrasado` / `Crítico` con color diferenciado.
- [x] `ultima_actividad` — fecha de última actividad o `-` si no hay.

## Filtros esperados

Según SRS `/docente/monitor` y F2.8:

- [ ] Búsqueda libre por alumno (nombre o correo) — **no implementado**: el tipo `MonitorFilters` no incluye campo `alumno` ni `email`.
- [ ] Filtro por comisión **legible** (no por ID técnico de texto libre) — **pendiente**: el filtro actual `comision_id` es un input de texto libre que expone el ID técnico. Debe reemplazarse por un selector de nombre o al menos un campo de búsqueda por nombre de comisión.
- [x] Filtro por materia — implementado con `Combobox` que muestra nombre + código.
- [ ] Filtro por regional — **no implementado**: no está en `MonitorFilters` ni en los filtros del componente.
- [ ] Filtro por actividad — **no implementado**: no está en `MonitorFilters` ni en los filtros del componente.
- [ ] Filtro por mínimo de actividad cumplida — **no implementado** (mencionado en F2.8).
- [x] Filtro por estado (`al_dia` / `atrasado` / `crítico`) — implementado.
- [x] Filtros de fecha desde/hasta — implementados. Nota: F2.9 asocia el rango de fechas al monitor de coordinación; F2.8 no los menciona explícitamente. Se mantiene hasta que se defina formalmente si aplican al monitor propio.

## Exportar

- [ ] Debe existir un botón de exportar en la pantalla — **no implementado en UI**: el servicio `exportarMonitor` existe en `monitores.ts` pero no hay botón en `MonitorPage.tsx`.
- [ ] La exportación debe respetar los mismos filtros activos.
- [ ] Debe mostrar Toast de éxito y error al exportar.
- [ ] El nombre del archivo debe ser claro para el usuario.

## UX/UI esperada

- [x] Respetar criterios transversales en `revisiones/criterios-transversales-ux-ui.md`.
- [ ] Mostrar error con Toast compartido si falla la carga de datos — **no implementado**: `MonitorPage.tsx` solo maneja `isLoading`, no el estado `error` del hook.
- [x] Estado de loading visible (`Spinner`).
- [x] Estado vacío claro: "No hay alumnos en el monitor."
- [ ] Filtro de comisión legible, no basado en ID técnico — ver Filtros.
- [ ] No mostrar IDs técnicos cuando existe nombre legible disponible — **pendiente**: el filtro `comision_id` expone el ID.
- [x] No usar `alert`, `confirm` ni prompts nativos del navegador.
- [ ] Tabla responsive (`overflow-x-auto`) — **verificar**: `MonitorTable` tiene `overflow-x-auto` en el contenedor.
- [x] Estado visual por alumno con badge coloreado (`al_dia` verde / `atrasado` amarillo / `crítico` rojo).

## Reglas de negocio

- [ ] El monitor propio (F2.8) muestra solo los alumnos de las materias asignadas al usuario autenticado — verificar scope en backend.
- [x] Los estados `al_dia`, `atrasado`, `crítico` son mutuamente excluyentes y se visualizan con badge diferenciado.
- [ ] Toda consulta del monitor debe auditarse según RN-23 — **verificar** si el backend registra `MONITOR_CONSULTAR`.
- [ ] Las consultas deben filtrar por `tenant_id` en backend — **verificar**.

## Estado actual observado

- [x] La ruta y el menú existen y piden `atrasados:ver`.
- [x] La tabla muestra columnas: alumno, comisión, materia, act. pendientes, entregas sin corregir, promedio, asistencias, estado y última actividad.
- [x] El estado de loading usa `Spinner` centralizado.
- [x] El estado vacío muestra mensaje de texto.
- [x] Los estados al_dia/atrasado/crítico tienen badge con color diferenciado.
- [x] El filtro de estado tiene selector con las tres opciones.
- [x] El filtro de materia usa `Combobox` con nombre legible.
- [ ] El filtro de comisión expone el ID técnico (input de texto libre `comision_id`) en lugar de un selector legible.
- [ ] No hay Toast de error si falla la carga de datos.
- [ ] No hay botón de exportar en la pantalla.
- [ ] No hay filtro de búsqueda por alumno.
- [ ] No hay filtro de regional ni de actividad.

## Pendientes para resolver en orden

1. [ ] Reemplazar el filtro `comision_id` (input de ID técnico) por un campo de búsqueda legible por nombre de comisión o selector.
2. [ ] Agregar manejo de error en `MonitorPage.tsx` con Toast compartido si falla la carga.
3. [ ] Agregar botón de exportar que consuma `exportarMonitor` y muestre Toast de éxito/error.
4. [ ] Agregar filtro de búsqueda libre por alumno (nombre o correo), según F2.8 y SRS.
5. [ ] Verificar scope del backend: que `/api/monitor/alumnos` filtre por las materias asignadas al docente autenticado y por `tenant_id`.
6. [ ] Verificar si el backend registra auditoria de consulta del monitor (RN-23).
7. [ ] Determinar con producto si se requieren los filtros de regional, actividad y mínimo de actividad cumplida para esta vista (F2.8 los menciona; sin decisión explícita no se implementan).
