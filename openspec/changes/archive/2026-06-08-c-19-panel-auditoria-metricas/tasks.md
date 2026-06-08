## 1. Repository — Aggregation queries for panel metrics

- [x] 1.1 Create `backend/app/repositories/panel_auditoria.py` with `PanelAuditoriaRepository`
- [x] 1.2 Implement `acciones_por_dia(fecha_desde, fecha_hasta, materia_id)` — GROUP BY date_trunc day
- [x] 1.3 Implement `comunicaciones_por_docente(fecha_desde, fecha_hasta, materia_id)` — GROUP BY actor, accion con filtro de códigos COMUNICACION_*
- [x] 1.4 Implement `interacciones_por_docente_materia(fecha_desde, fecha_hasta, actor_id)` — GROUP BY actor, materia, accion
- [x] 1.5 Implement `ultimas_acciones(limit, offset, filters)` con límite configurable (max 1000)

## 2. Service — Panel auditoria business logic

- [x] 2.1 Create `backend/app/services/panel_auditoria.py` with `PanelAuditoriaService`
- [x] 2.2 Implement scope `(propio)` para COORDINADOR: detectar rol vía Asignacion, filtrar materias del usuario
- [x] 2.3 Implement método `get_acciones_por_dia` que aplica scope y llama al repo
- [x] 2.4 Implement método `get_comunicaciones_por_docente` que aplica scope y llama al repo
- [x] 2.5 Implement método `get_interacciones_por_docente_materia` que aplica scope y llama al repo
- [x] 2.6 Implement método `get_ultimas_acciones` que aplica scope y llama al repo

## 3. Schemas — Pydantic request/response models

- [x] 3.1 Create `backend/app/schemas/panel_auditoria.py` with response models for each aggregation
- [x] 3.2 Add `AccionesPorDiaResponse`, `ComunicacionesPorDocenteResponse`, `InteraccionesResponse`, `UltimasAccionesResponse`
- [x] 3.3 All schemas with `extra='forbid'` and `from_attributes=True`

## 4. Router — API endpoints

- [x] 4.1 Create `backend/app/api/v1/routers/auditoria.py` with prefix `/api/v1/auditoria`
- [x] 4.2 Implement `GET /panel/acciones-por-dia` con filtros fecha_desde, fecha_hasta, materia_id
- [x] 4.3 Implement `GET /panel/comunicaciones-por-docente` con filtros fecha_desde, fecha_hasta, materia_id
- [x] 4.4 Implement `GET /panel/interacciones-por-docente-materia` con filtros fecha_desde, fecha_hasta, actor_id
- [x] 4.5 Implement `GET /panel/ultimas-acciones` con max_results (default 200, max 1000)
- [x] 4.6 Registrar router en `app/main.py`
- [x] 4.7 Agregar dependency `get_panel_auditoria_service` en `core/dependencies.py`

## 5. Tests

- [x] 5.1 Create `backend/tests/test_c19_panel_auditoria.py` with test data fixtures
- [x] 5.2 Tests: acciones por día dentro de rango, filtro por materia, rango vacío
- [x] 5.3 Tests: comunicaciones por docente agrupadas, filtro por materia
- [x] 5.4 Tests: interacciones por docente×materia, filtros por fecha y actor
- [x] 5.5 Tests: últimas acciones con default limit 200, custom limit 50, cap at 1000
- [x] 5.6 Tests: scope `(propio)` — COORDINADOR solo ve sus materias, ADMIN ve todo, FINANZAS ve todo
