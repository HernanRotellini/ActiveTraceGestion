# Checklist - Pantalla Avisos

## Fuentes revisadas

- `docs/SRS.md`: `/coordinacion/avisos`; requiere `avisos:ver` / `avisos:gestionar`; operaciones: listar, crear, editar, activar/desactivar, estadísticas de lectura.
- `knowledge-base/06_funcionalidades.md`: F5.x — Avisos institucionales: publicar, alcance por rol/materia/cohorte/global, confirmación de lectura (requiere_ack), seguimiento.
- `knowledge-base/11_historias_de_usuario.md`: HU-21 publicar aviso; HU-22 confirmar lectura; HU-23 ver avisos pendientes de confirmación.
- `backend/app/api/v1/routers/avisos.py`: endpoints reales confirmados.
- `backend/app/schemas/aviso.py`: schemas reales confirmados.
- `revisiones/criterios-transversales-ux-ui.md`

## Alcance esperado

- Gestión admin (`/coordinacion/avisos`): listar todos los avisos (activos e inactivos), crear, editar, activar/desactivar, ver stats de confirmación.
- Vista docente/alumno: avisos visibles propios, pendientes de ACK, confirmar lectura.
- Alcances válidos: `Global`, `PorMateria`, `PorCohorte`, `PorRol`.
- Severidades: `Info`, `Advertencia`, `Critico`.

## Endpoints reales del backend

| Operación | Endpoint | Permisos |
|-----------|----------|----------|
| Listar visibles | `GET /api/avisos` | autenticado |
| Pendientes ACK | `GET /api/avisos/pendientes-ack` | autenticado |
| Confirmar lectura | `POST /api/avisos/{id}/ack` | autenticado |
| Listar todos (admin) | `GET /api/admin/avisos?alcance=&severidad=&activo=` | `avisos:ver` |
| Crear | `POST /api/admin/avisos` | `avisos:gestionar` |
| Detalle (admin) | `GET /api/admin/avisos/{id}` | `avisos:ver` |
| Actualizar | `PUT /api/admin/avisos/{id}` | `avisos:gestionar` |
| Desactivar | `DELETE /api/admin/avisos/{id}` | `avisos:gestionar` |
| Stats | `GET /api/admin/avisos/{id}/stats` | `avisos:ver` |

## Tipos

- [ ] `Aviso` tenía campos ficticios no presentes en el backend: `estado`, `contenido`, `scope`, `scope_valor`, `autor_nombre`, `publicado_en`, `acks`. Reemplazado por tipos separados `AvisoResponse` (admin) y `AvisoListResponse` (vista pública).
- [ ] Faltaba tipo `AvisoStatsResponse` con `total_acks` y `usuarios_sin_confirmar`.
- [ ] `AvisosListFilters` tenía `fecha_desde`, `fecha_hasta` — no soportadas por el backend. Corregido a `alcance?`, `severidad?`, `activo?`.
- [ ] `AvisosListFilters` tenía `page` y `limit` — no soportados por el backend.

## Servicios (services/api.ts)

- [ ] `listarAvisos`: `GET /admin/avisos` → debe ser `GET /api/admin/avisos` (falta `/api/`).
- [ ] `obtenerAviso`: `GET /admin/avisos/${id}` → `GET /api/admin/avisos/${id}`.
- [ ] `crearAviso`: `POST /admin/avisos` → `POST /api/admin/avisos`.
- [ ] `actualizarAviso`: `PUT /admin/avisos/${id}` → `PUT /api/admin/avisos/${id}`.
- [ ] `publicarAviso`: `PUT /admin/avisos/${id}` → `PUT /api/admin/avisos/${id}`.
- [ ] `archivarAviso`: `DELETE /admin/avisos/${id}` → `DELETE /api/admin/avisos/${id}`.
- [ ] Faltaba función para stats: `GET /api/admin/avisos/${id}/stats`.

## Componentes

### AvisosListPage
- [x] Muestra lista de avisos con título, severidad badge, fecha, alcance, requiere_ack.
- [x] Spinner durante carga.
- [x] Estado vacío: "No hay avisos registrados."
- [x] Enlace a detalle desde cada card.
- [ ] Error mostrado como full-page, no como Toast.
- [ ] Filtro `page`/`limit` no soportado por el backend.
- [ ] Falta filtro por `alcance` (soportado por el backend).

### AvisoDetailPage
- [ ] Usa `aviso.estado` (no existe en backend) para controlar botones Publicar/Archivar. Debe usar `aviso.activo` (boolean).
- [ ] Muestra `aviso.contenido` (no existe). Debe usar `aviso.cuerpo`.
- [ ] Muestra `aviso.scope`/`aviso.scope_valor` (no existen). Debe usar `aviso.alcance`, `aviso.materia_id`, `aviso.rol_destino`.
- [ ] Muestra `aviso.autor_nombre` y `aviso.publicado_en` (no existen en `AvisoResponse`).
- [ ] Sección "Seguimiento de lectura" usa `aviso.acks` (no existe). Debe usar `GET /api/admin/avisos/{id}/stats`.
- [ ] `AckProgressBar` toma `AckStatus[]` pero el backend retorna sólo conteos en stats.

### AvisoFormPage
- [ ] Usa concepto legacy `scope`/`scope_valor` en lugar de `alcance` del backend.
- [ ] `por_usuario` scope no tiene soporte en el backend (se mapea incorrectamente a `Global`).
- [ ] Falta selector de `severidad` (Info / Advertencia / Crítico).
- [ ] Falta checkbox `requiere_ack`.
- [ ] Falta campo `fin_en` (fecha de fin de aviso).
- [ ] `PorCohorte` alcance no es recolectado en el formulario.
- [ ] El label "Comisión ID" para `por_comision` es incorrecto — es `materia_id`.

### AckProgressBar
- [ ] Actualmente espera `AckStatus[]` con detalle de cada usuario. El backend solo provee `total_acks` y `usuarios_sin_confirmar` (lista de UUIDs). Debe actualizarse a recibir conteos.

## UX/UI esperada

- [x] Badge de severidad con colores diferenciados.
- [x] Spinner durante carga.
- [x] Estado vacío claro.
- [ ] Error de carga con Toast (actualmente full-page).
- [x] No usa `alert`, `confirm` ni prompts nativos.
- [ ] `AvisoFormPage` sin confirmación de éxito al crear/editar (no hay Toast de éxito).

## Reglas de negocio

- [x] Alcances válidos: Global, PorMateria, PorCohorte, PorRol — validados en backend.
- [x] `PorMateria` requiere `materia_id`; `PorCohorte` requiere `cohorte_id`; `PorRol` requiere `rol_destino`.
- [x] `requiere_ack`: si true, el aviso requiere confirmación de lectura.
- [x] Desactivar = soft delete (DELETE en el backend es un soft-delete, no borrado permanente).
- [x] Toda acción auditable pasa por el tenant del usuario autenticado.

## Pendientes resueltos en esta revisión

1. [x] URLs corregidas: añadido prefijo `/api/` a todas las funciones del servicio
2. [x] Tipos corregidos: `AvisoResponse`, `AvisoListResponse`, `AvisoStatsResponse` alineados con el backend
3. [x] `AvisosListPage`: error con Toast, filtros alineados con backend, añadido filtro `alcance`
4. [x] `AvisoDetailPage`: usa `activo`, `cuerpo`, `alcance` del backend; stats desde endpoint real
5. [x] `AckProgressBar`: actualizado para recibir conteos en lugar de array de AckStatus
6. [x] `AvisoFormPage`: alcance directo (Global/PorMateria/PorCohorte/PorRol), añadidos severidad, requiere_ack, fin_en
7. [x] Añadido hook `useAvisoStats` y función `obtenerStatsAviso`

## Pendientes sin resolver (requieren decisión de producto)

1. [ ] Pantalla de confirmación de lectura para usuarios no-admin (`POST /api/avisos/{id}/ack` existe pero no hay UI).
2. [ ] Vista `/avisos` para docentes/alumnos (`GET /api/avisos`) — sin pantalla propia en el frontend.
3. [ ] Vista de pendientes-ack (`GET /api/avisos/pendientes-ack`) — sin pantalla propia.
