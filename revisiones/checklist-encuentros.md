# Checklist — Encuentros

> Fuentes: `knowledge-base/06_funcionalidades.md` (Épica 6, F6.1–F6.5), `knowledge-base/05_reglas_de_negocio.md` (RN-13, RN-14), `backend/app/api/v1/routers/encuentros.py`, `backend/app/schemas/encuentro.py`, `backend/app/models/encuentro.py`

## Contratos de API (según backend)

- [x] `GET /api/v1/encuentros/slots` — lista slots (filter: materia_id) → `SlotEncuentroResponse[]`
- [x] `POST /api/v1/encuentros/slots` — crear slot recurrente → `SlotEncuentroResponse`
- [x] `GET /api/v1/encuentros/instancias` — lista instancias (filter: materia_id) → `InstanciaEncuentroResponse[]`
- [x] `POST /api/v1/encuentros/instancias` — crear instancia única → `InstanciaEncuentroResponse`
- [x] `PATCH /api/v1/encuentros/instancias/{id}` — actualizar estado/meet_url/video_url/comentario
- [x] `GET /api/v1/encuentros/instancias/{id}/html` — bloque HTML para publicar en LMS
- [x] `GET /api/v1/encuentros/admin/instancias` — vista admin (filters: materia_id, fecha_desde, fecha_hasta, estado)
- [ ] No existe `GET /api/v1/encuentros/instancias/{id}` — se resuelve con fetch de lista + find por id

## Tipos correctos

- [x] `EstadoInstancia` = `'Programado' | 'Realizado' | 'Cancelado'` (casing exacto del enum backend)
- [x] `DiaSemana` = `'Lunes' | 'Martes' | 'Miercoles' | 'Jueves' | 'Viernes' | 'Sabado'`
- [x] `SlotEncuentroResponse` con `asignacion_id`, `materia_id`, `titulo`, `dia_semana`, `hora`, `fecha_inicio`, `cant_semanas`, `meet_url`, `vig_desde`, `vig_hasta`
- [x] `InstanciaEncuentroResponse` con `slot_id?`, `materia_id`, `fecha`, `hora`, `titulo`, `estado`, `meet_url?`, `video_url?`, `comentario?`
- [x] `InstanciaEncuentroUpdate` con campos opcionales `estado`, `meet_url`, `video_url`, `comentario`
- [x] Eliminados: `comision_id`, `comision_nombre`, `aula`, `duracion_minutos`, `slots`, `instancias`, `guardias` (no existen en el backend)
- [x] Eliminados: `SlotHorario`, `InstanciaDictado`, `Guardia` (conceptos inventados)

## Servicios

- [x] URL base `/api/v1/encuentros` (no `/encuentros` sin prefix)
- [x] `listarSlots(filters?)` — `GET /api/v1/encuentros/slots`
- [x] `crearSlot(payload)` — `POST /api/v1/encuentros/slots`
- [x] `listarInstancias(filters?)` — `GET /api/v1/encuentros/instancias`
- [x] `crearInstancia(payload)` — `POST /api/v1/encuentros/instancias`
- [x] `actualizarInstancia(id, update)` — `PATCH /api/v1/encuentros/instancias/{id}`
- [x] `generarHtml(instanciaId)` — `GET /api/v1/encuentros/instancias/{id}/html`
- [x] `adminListarInstancias(filters?)` — `GET /api/v1/encuentros/admin/instancias`
- [x] Eliminados: `agregarGuardia`, `quitarGuardia`, `eliminarEncuentro` (no existen en backend)

## Hooks

- [x] `useSlotsList(filters?)` — query key `['encuentros-slots', filters]`
- [x] `useInstanciasList(filters?)` — query key `['encuentros-instancias', filters]`
- [x] `useAdminInstancias(filters?)` — query key `['encuentros-admin', filters]`
- [x] `useCrearSlot()` — invalida slots + instancias + admin
- [x] `useCrearInstancia()` — invalida instancias + admin
- [x] `useActualizarInstancia()` — invalida instancias + admin
- [x] Eliminados: `useEliminarEncuentro`, `useAgregarGuardia`, `useQuitarGuardia`

## EncuentrosListPage (F6.5 — Vista admin)

- [x] Usa `useAdminInstancias` (vista transversal del tenant)
- [x] Filtros: fecha_desde, fecha_hasta, estado, materia_id
- [x] Columnas: título, fecha, hora, estado (badge de color), meet_url, acciones
- [x] Estados con colores: Programado=azul, Realizado=verde, Cancelado=gris
- [x] Modal inline para editar instancia (estado, meet_url, video_url, comentario)
- [x] Toast de error de carga y de actualización

## EncuentroDetailPage (F6.3 — Editar instancia)

- [x] Fetch via `useAdminInstancias()` + find por id (no hay endpoint single)
- [x] Muestra: título, estado (badge), fecha, hora, meet_url, video_url, comentario
- [x] Formulario de edición: estado, meet_url, video_url, comentario
- [x] Toast éxito/error al guardar
- [x] Link de vuelta a lista

## Criterios transversales

- [x] Identidad desde JWT (no URL/body)
- [x] Multi-tenancy: backend filtra por tenant en cada query
- [x] RBAC: `encuentros:ver` / `encuentros:gestionar` (declarados en el backend)
- [x] Soft delete: `PATCH` para cambiar estado (no hay DELETE)
- [x] Auditoría: cambios de estado auditados por el backend
- [x] Sin `any` en TypeScript
