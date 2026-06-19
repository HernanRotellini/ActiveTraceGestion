# Checklist - Pantalla Equipos Docentes

## Fuentes revisadas

- `docs/SRS.md`: `/coordinacion/equipos-docentes`; requiere `equipos:ver` / `equipos:gestionar`; operaciones: listar asignaciones, asignación masiva, clonar, actualizar vigencia, exportar CSV.
- `knowledge-base/06_funcionalidades.md`: F4.1 Listar equipos por materia; F4.2 Crear/modificar asignaciones; F4.3 Asignación masiva; F4.4 Clonar equipo; F4.5 Actualizar vigencia; F4.6 Exportar; F4.7 Ver mis equipos.
- `knowledge-base/11_historias_de_usuario.md`: HU-16 listar docentes de una materia; HU-17 asignación masiva; HU-18 clonar equipo entre cohortes; HU-19 actualizar vigencia; HU-20 exportar CSV equipo.
- `knowledge-base/05_reglas_de_negocio.md`: RN-23 auditoría; roles válidos: PROFESOR, TUTOR, COORDINADOR, NEXO.
- `backend/app/api/v1/routers/equipos.py`: endpoints reales en `/api/equipos/`.
- `backend/app/api/v1/routers/asignaciones.py`: `GET /api/asignaciones` para listar.
- `backend/app/schemas/equipos.py`: schemas reales confirmados.
- `revisiones/criterios-transversales-ux-ui.md`

## Alcance esperado

La sección `/coordinacion/equipos-docentes` cubre:
- **Listado** de asignaciones docentes: tabla paginada con filtros por materia, docente y rol.
- **Crear asignación** (F4.2/F4.3): formulario masivo que asigna múltiples docentes a materia + carrera + cohorte + rol + vigencia + comisiones.
- **Clonar equipo** (F4.4): copia asignaciones de una combinación materia/carrera/cohorte origen a un destino.
- **Actualizar vigencia** (F4.5): modifica fechas de vigencia para un grupo de asignaciones de una materia/carrera/cohorte.
- **Exportar CSV** (F4.6): requiere materia_id, carrera_id, cohorte_id; no es un export global.
- **Mis equipos** (F4.7): `GET /api/equipos/mis-equipos` (vista docente); pendiente de pantalla propia en el frontend.

## Permisos esperados

- [x] Ruta `/coordinacion/equipos-docentes` protegida con `equipos:ver` (`PermissionGuard`).
- [x] Menú lateral muestra "Equipos docentes" solo con `equipos:ver`.
- [x] Backend: `GET /api/asignaciones` requiere `equipos:ver`; `POST /api/equipos/asignacion-masiva`, `POST /api/equipos/clonar`, `PATCH /api/equipos/vigencia` requieren `equipos:gestionar`; `GET /api/equipos/exportar` requiere `equipos:ver`.
- [x] Backend: identidad y tenant siempre desde JWT verificado.

## Endpoints reales del backend

| Operación | Endpoint real | Qué necesita |
|-----------|---------------|--------------|
| Listar asignaciones | `GET /api/asignaciones` | `materia_id?`, `usuario_id?`, `rol?` |
| Crear masiva | `POST /api/equipos/asignacion-masiva` | `{ usuario_ids, materia_id, carrera_id, cohorte_id, rol, comisiones?, desde, hasta? }` |
| Clonar | `POST /api/equipos/clonar` | `{ origen: { materia_id, carrera_id, cohorte_id }, destino: { carrera_id, cohorte_id, desde, hasta? } }` |
| Vigencia | `PATCH /api/equipos/vigencia` | `{ materia_id, carrera_id, cohorte_id, desde?, hasta? }` |
| Exportar CSV | `GET /api/equipos/exportar` | `materia_id` (req), `carrera_id` (req), `cohorte_id` (req) |
| Mis equipos | `GET /api/equipos/mis-equipos` | — |

> **No existe endpoint** `GET /api/equipos-docentes/{id}` ni `PATCH /api/equipos-docentes/{id}`. El concepto de "equipo" como entidad con ID propio no está en el backend.

## Tipos

- [x] `Asignacion.rol` usaba `'titular' | 'adjunto' | 'auxiliar' | 'jefe_tp'` — valores incorrectos. Los roles reales son `'PROFESOR' | 'TUTOR' | 'COORDINADOR' | 'NEXO'`.
- [x] `AsignacionMasivaPayload` era `{ equipo_id, usuarios: [{ usuario_id, rol }] }` — no coincide con el backend (`AsignacionMasivaRequest`). Tipo obsoleto eliminado.
- [x] `ClonePayload` usaba `{ origen_equipo_id, destino_materia_id, periodo }` — completamente incorrecto. Corregido a `{ origen: { materia_id, carrera_id, cohorte_id }, destino: { carrera_id, cohorte_id, desde, hasta? } }`.
- [x] `VigenciaPayload` usaba `{ asignacion_id, desde, hasta }` — incorrecto. Corregido a `{ materia_id, carrera_id, cohorte_id, desde?, hasta? }`.

## Servicios (services/api.ts)

- [x] `listarAsignaciones` llamaba a `GET /asignaciones` (sin prefijo `/api/`) — corregido a `GET /api/asignaciones`.
- [x] `crearAsignacionesEquipo` llamaba a `POST /equipos/asignacion-masiva` — corregido a `POST /api/equipos/asignacion-masiva`.
- [x] `clonarEquipo` llamaba a `POST /equipos-docentes/clonar` con payload incorrecto — corregido a `POST /api/equipos/clonar` con `CloneEquipoRequest`.
- [x] `actualizarVigencia` llamaba a `PATCH /equipos-docentes/asignaciones/{id}/vigencia` — corregido a `PATCH /api/equipos/vigencia` sin path param.
- [x] `exportarEquiposCSV` llamaba a `GET /equipos-docentes/exportar` — corregido a `GET /api/equipos/exportar`.
- [x] Funciones `listarEquipos`, `obtenerEquipo`, `crearEquipo`, `actualizarEquipo`, `eliminarEquipo`, `asignacionMasiva` llamaban a endpoints que no existen en el backend. Eliminadas.

## Componentes

### AsignacionMasivaModal
- [x] Usaba roles incorrectos: `['titular', 'adjunto', 'auxiliar', 'jefe_tp']`. Corregido a `['PROFESOR', 'TUTOR', 'COORDINADOR', 'NEXO']`.
- [x] No mostraba errores de la mutación. Añadido Toast de error.
- [x] Reescrito para usar `useCrearAsignacionesEquipo` (endpoint correcto) y recoger carrera, cohorte, materia, docentes, rol, vigencia.

### ClonarModal
- [x] Enviaba payload `{ origen_equipo_id, destino_materia_id, periodo }` — completamente incorrecto. Reescrito con payload correcto: `{ origen: { materia_id, carrera_id, cohorte_id }, destino: { carrera_id, cohorte_id, desde, hasta? } }`.
- [x] Ahora recoge datos de origen (carrera/cohorte/materia) y destino (carrera/cohorte/desde/hasta) en el formulario.
- [x] Añadido Toast de error.

### EquiposListPage
- [x] Muestra tabla de asignaciones con columnas: Docente, Rol, Materia, Carrera, Cohorte, Comisiones, Vigencia, Estado.
- [x] Filtros funcionales: materia (Combobox), docente (Combobox), rol (select).
- [x] Badge de estado vigente/vencida.
- [x] Toast de error si falla la carga.
- [x] Spinner durante la carga.
- [x] Estado vacío: "No hay asignaciones registradas."
- [x] URL del servicio corregida a `/api/asignaciones`.
- [ ] No tiene enlace desde filas al detalle de asignación individual (pendiente de decisión de producto — no hay endpoint de detalle por equipo).

### EquipoFormPage (Nueva asignación)
- [x] Recoge: carrera, cohorte, materia, docentes (múltiples), rol, comisiones, desde, hasta.
- [x] Roles correctos: PROFESOR, TUTOR, COORDINADOR, NEXO.
- [x] Validación con Toast de error.
- [x] Toast de éxito al crear.
- [x] Redirige al listado tras crear.
- [x] URL del servicio corregida a `/api/equipos/asignacion-masiva`.

### EquipoDetailPage
- [ ] Llama a `GET /equipos-docentes/{id}` que no existe en el backend — la página siempre muestra "Equipo no encontrado". No hay endpoint de detalle por equipo.
- [ ] Pendiente de backend: si se implementa un endpoint de detalle, la página puede completarse.
- [ ] Acción "Finalizar/Reactivar" usaba endpoint inexistente con payload incorrecto. Simplificada.

## Exportar CSV

- [ ] `ExportCsvButton` no pasa los 3 parámetros requeridos por el backend (`materia_id`, `carrera_id`, `cohorte_id`). Como el botón está en `EquipoDetailPage` (sin contexto de equipo disponible), exportar CSV queda pendiente hasta que el backend tenga endpoint de detalle o la UI sea refactorizada.

## UX/UI esperada

- [x] Respetar criterios transversales en `revisiones/criterios-transversales-ux-ui.md`.
- [x] Toast de error si falla la carga del listado.
- [x] Spinner durante carga del listado.
- [x] Estado vacío claro en el listado.
- [x] No muestra IDs técnicos en la tabla (usa lookups por materia, carrera, cohorte, usuario).
- [x] Badge coloreado para vigencia.
- [x] Tabla responsive con `overflow-x-auto`.
- [x] No usa `alert`, `confirm` ni prompts nativos.

## Reglas de negocio

- [x] Los roles de asignación son PROFESOR, TUTOR, COORDINADOR, NEXO — no "titular/adjunto/auxiliar/jefe_tp".
- [x] Toda asignación tiene `materia_id`, `carrera_id`, `cohorte_id` como contexto.
- [x] El estado de vigencia (`vigente`/`vencida`) se calcula por fechas en el backend y se muestra en badge.
- [x] La exportación CSV requiere los tres ejes de contexto (materia, carrera, cohorte).

## Pendientes resueltos en esta revisión

1. [x] URL de `listarAsignaciones`: `/asignaciones` → `/api/asignaciones`
2. [x] URL de `crearAsignacionesEquipo`: `/equipos/asignacion-masiva` → `/api/equipos/asignacion-masiva`
3. [x] URL de `clonarEquipo`: `/equipos-docentes/clonar` → `/api/equipos/clonar`
4. [x] URL de `actualizarVigencia`: `/equipos-docentes/asignaciones/{id}/vigencia` → `/api/equipos/vigencia`
5. [x] URL de `exportarEquiposCSV`: `/equipos-docentes/exportar` → `/api/equipos/exportar`
6. [x] Tipos: `Asignacion.rol` corregido a valores reales del backend
7. [x] Tipos: `ClonePayload` y `VigenciaPayload` corregidos para coincidir con el backend
8. [x] `AsignacionMasivaModal`: roles corregidos
9. [x] `ClonarModal`: reescrito con payload correcto

## Pendientes sin resolver (requieren backend o decisión de producto)

1. [ ] `EquipoDetailPage`: No existe endpoint `GET /api/equipos/{id}`. La vista de detalle está simplificada hasta que el backend lo implemente.
2. [ ] Exportar CSV: requiere que la UI exponga los tres filtros de contexto (materia + carrera + cohorte) antes de exportar.
3. [ ] `GET /api/equipos/mis-equipos`: No tiene pantalla propia en el frontend. Pendiente de decisión de UX.
