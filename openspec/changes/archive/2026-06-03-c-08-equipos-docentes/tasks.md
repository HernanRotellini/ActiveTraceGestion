## 1. Schemas

- [x] 1.1 Create `backend/app/schemas/equipos.py` with Pydantic DTOs: `AsignacionMasivaRequest` (usuario_ids list, materia_id, carrera_id, cohorte_id, rol, desde, hasta), `CloneEquipoRequest` (origen/destino con materia_id, carrera_id, cohorte_id, desde, hasta), `VigenciaUpdateRequest` (materia_id, carrera_id, cohorte_id, desde opcional, hasta opcional), `VigenciaUpdateResponse` (asignaciones_afectadas: int)

## 2. Service

- [x] 2.1 Create `backend/app/services/equipos.py` with `EquipoService`:
  - `list_mis_equipos(usuario_id, estado, materia_id, rol, carrera_id, cohorte_id)` — lista asignaciones del usuario con filtros opcionales; si `estado=vigente` filtra por `estado_vigencia` computado
  - `asignacion_masiva(usuario_ids, materia_id, carrera_id, cohorte_id, rol, desde, hasta)` — valida que todos los usuarios existan, luego crea asignaciones en batch; si algún usuario no existe → 404 sin crear ninguna
  - `clone_equipo(origen, destino)` — busca asignaciones vigentes del origen, las duplica con nuevas fechas; si origen no tiene asignaciones → lista vacía (200)
  - `update_vigencia_equipo(materia_id, carrera_id, cohorte_id, desde, hasta)` — actualiza fechas de todas las asignaciones del equipo; si `desde` o `hasta` es `None` no se modifica ese campo; retorna cantidad de asignaciones afectadas
  - `export_equipo_csv(materia_id, carrera_id, cohorte_id)` — genera CSV con cabeceras `docente,rol,materia,carrera,cohorte,comisiones,desde,hasta,estado_vigencia`
  - Helper `_audit_action(accion, detalle)` — placeholder que loguea en JSON structurado (reemplazar por C-05 cuando esté listo)

## 3. Router

- [x] 3.1 Create `backend/app/api/v1/routers/equipos.py` con prefix `/api/equipos`:
  - `GET /mis-equipos` — sin guard `equipos:asignar` (cualquier rol docente autenticado), acepta query params `estado`, `materia_id`, `rol`, `carrera_id`, `cohorte_id`
  - `POST /asignacion-masiva` — guard `equipos:asignar`, 201 con lista de asignaciones creadas
  - `POST /clonar` — guard `equipos:asignar`, 201 con lista de asignaciones clonadas
  - `PATCH /vigencia` — guard `equipos:asignar`, 200 con `VigenciaUpdateResponse`
  - `GET /exportar` — guard `equipos:asignar`, 200 con `StreamingResponse` CSV (requiere materia_id, carrera_id, cohorte_id query params obligatorios → 422 si faltan)
- [x] 3.2 Wire router en `backend/app/main.py`

## 4. Tests

- [x] 4.1 Tests for `mis-equipos`: docente ve sus asignaciones, filtra por estado/materia, multi-tenant isolation
- [x] 4.2 Tests for `asignacion-masiva`: creación batch exitosa, usuario inexistente → 404, duplicate check, 403 sin permiso
- [x] 4.3 Tests for `clonar`: clonado exitoso con fechas correctas, origen sin asignaciones → lista vacía, 403 sin permiso
- [x] 4.4 Tests for `vigencia`: update en bloque, solo desde (hasta no cambia), 403 sin permiso
- [x] 4.5 Tests for `exportar`: CSV generado con cabeceras correctas, contenido incluye asignaciones del equipo, 422 sin parámetros

## 5. Verification

- [x] 5.1 Run full test suite: all C-08 tests pass (16/16), no regressions on existing tests (168/170 pass, 2 pre-existing migrations failures unrelated to C-08)
- [ ] 5.2 Run lint and type checks (if tools available) — ⚠️ skipped, no lint tool configured
