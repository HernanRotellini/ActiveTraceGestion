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
- [x] Backend: `GET /api/analisis/monitor` filtra por asignaciones del usuario autenticado cuando no tiene scope global (COORDINADOR/ADMIN). Roles sin scope global usan `monitor_por_asignaciones` con los `asignacion_ids` propios.
- [x] Backend: identidad desde `current_user` inyectado por JWT verificado; `tenant_id` y `user_id` salen de la sesión, nunca de parámetros.
- [x] Backend: toda consulta usa `self.tenant_id` scoped en el repositorio.

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

- [x] Búsqueda libre por alumno (nombre o correo) — campo `busqueda` agregado al tipo y al componente de filtros.
- [x] Filtro por comisión **legible** — reemplazado `comision_id` (input de ID técnico) por `comision` (input de texto por nombre de comisión), alineado con el parámetro real del backend.
- [x] Filtro por materia — implementado con `Combobox` que muestra nombre + código.
- [x] Filtro por regional — campo `regional` agregado al tipo y al componente de filtros.
- [x] Filtro por actividad — campo `actividad` agregado al tipo y al componente de filtros.
- [x] Filtro por mínimo de actividad cumplida — campo `min_actividad_cumplida` agregado al tipo y al componente de filtros.
- [x] El filtro de estado (`atrasado` boolean) se refleja en el badge de la tabla (Atrasado / Al día). El backend no expone un filtro de estado como query param; el estado se deriva del campo `atrasado` del `MonitorItem`.

## Exportar

- [ ] No existe endpoint de exportación para el monitor en el backend (`/api/analisis/monitor/exportar`). El servicio de exportación fue removido del frontend al realinear con el backend real. Pendiente de decisión de producto para implementar un endpoint de exportación CSV.

## UX/UI esperada

- [x] Respetar criterios transversales en `revisiones/criterios-transversales-ux-ui.md`.
- [x] Mostrar error con Toast compartido si falla la carga de datos — agregado en `MonitorPage.tsx`.
- [x] Estado de loading visible (`Spinner`).
- [x] Estado vacío claro: "No hay alumnos en el monitor."
- [x] Filtro de comisión legible — reemplazado por campo de texto `comision` por nombre.
- [x] No mostrar IDs técnicos — el filtro `comision_id` fue eliminado.
- [x] No usar `alert`, `confirm` ni prompts nativos del navegador.
- [x] Tabla responsive con `overflow-x-auto`.
- [x] Estado visual por alumno con badge coloreado (Atrasado rojo / Al día verde).

## Reglas de negocio

- [x] El monitor propio (F2.8) muestra solo los alumnos de las materias asignadas al usuario autenticado — el backend usa `monitor_por_asignaciones` con los `asignacion_ids` propios cuando el rol no tiene scope global.
- [x] El estado `atrasado` (boolean) se visualiza con badge diferenciado: Atrasado (rojo) / Al día (verde).
- [x] Toda consulta del monitor se audita con `ANALISIS_CONSULTAR` (verificado en `AnalisisService.get_monitor`).
- [x] Las consultas filtran por `self.tenant_id` — el repositorio es tenant-scoped.

## Estado actual observado

- [x] La ruta y el menú existen y piden `atrasados:ver`.
- [x] La tabla muestra columnas alineadas con el backend: alumno, email, comisión, regional, total actividades, aprobadas, pendientes, estado (Atrasado/Al día).
- [x] El estado de loading usa `Spinner` centralizado.
- [x] El estado vacío muestra mensaje de texto.
- [x] El badge de estado usa `atrasado` (boolean) del backend: Atrasado (rojo) / Al día (verde).
- [x] El filtro de materia usa `Combobox` con nombre legible.
- [x] El filtro de comisión es por nombre (texto), no por ID técnico.
- [x] El filtro de búsqueda libre por alumno/email existe (`busqueda`).
- [x] Filtros de regional, actividad y mínimo de actividades cumplidas implementados.
- [x] Toast de error si falla la carga de datos.
- [x] URL del servicio corregida a `/api/analisis/monitor`.
- [x] Tipo de respuesta corregido a `MonitorResponse { items, total }`.
- [ ] No hay endpoint de exportación en el backend — pendiente de decisión de producto.

## Pendientes para resolver en orden

1. [ ] Implementar endpoint de exportación CSV en el backend (`/api/analisis/monitor/exportar`) si se decide agregar la funcionalidad. Hasta entonces, sin botón de exportar en la pantalla.
