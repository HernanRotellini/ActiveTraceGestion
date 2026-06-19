# Checklist — Tareas Internas

> Fuentes: `knowledge-base/06_funcionalidades.md` (C-15), `knowledge-base/05_reglas_de_negocio.md`, `knowledge-base/03_actores_y_roles.md`, `docs/PRD.md`

## Contratos de API (según backend)

- [x] `GET /api/tareas` — lista tareas con filtros (`asignado_a`, `asignado_por`, `materia_id`, `estado`, `search`, `limit`, `offset`)
- [x] `GET /api/tareas/mis` — tareas asignadas al usuario actual (`limit`, `offset`)
- [x] `GET /api/tareas/{id}` — detalle con comentarios embebidos (`TareaDetailResponse`)
- [x] `POST /api/tareas` — crear tarea (`titulo`, `descripcion`, `asignado_a`, `materia_id?`, `contexto_id?`)
- [x] `PATCH /api/tareas/{id}/estado` — cambiar estado (`estado: TareaEstado`)
- [x] `POST /api/tareas/{id}/delegar` — reasignar tarea (`asignado_a: uuid`)
- [x] `POST /api/tareas/{id}/comentarios` — agregar comentario (`texto: string`)

## Tipos correctos

- [x] `TareaEstado` = `'Pendiente' | 'En progreso' | 'Resuelta' | 'Cancelada'` (casing exacto)
- [x] `ComentarioResponse` usa campo `texto` (no `contenido`), `autor_id` (UUID), `created_at`
- [x] `TareaResponse` tiene `asignado_a` y `asignado_por` como UUIDs (sin nombre resuelto)
- [x] `TareaDetailResponse` extiende `TareaResponse` con `comentarios: ComentarioResponse[]`
- [x] Sin campo `prioridad`, sin `fecha_limite`, sin `asignado_nombre`

## Servicios

- [x] Todas las URLs incluyen `/api/` prefix
- [x] `cambiarEstadoTarea` usa `PATCH /api/tareas/{id}/estado`
- [x] `delegarTarea` usa `POST /api/tareas/{id}/delegar`
- [x] `crearComentario` usa `POST /api/tareas/{id}/comentarios` con `{ texto }`
- [x] Eliminada función `actualizarTarea` (no existe en backend)
- [x] Eliminada función `listarComentarios` (comentarios vienen embebidos en el detalle)

## Hooks

- [x] `useTareasList` — query key `['tareas-internas', filters]`
- [x] `useTarea(id)` — query key `['tarea', id]`
- [x] `useCrearTarea` — invalida `['tareas-internas']`
- [x] `useCambiarEstadoTarea` — invalida lista + detalle
- [x] `useDelegarTarea` — invalida lista + detalle
- [x] `useCrearComentario(tareaId)` — invalida `['tarea', tareaId]` (NO una query separada de comentarios)

## TareasListPage

- [x] Filtros disponibles: `estado`, `asignado_a`, `search` (texto libre)
- [x] Columnas: Título, Estado, Asignado a (nombre via usuariosById), Asignado por (nombre via usuariosById), Creada
- [x] Estados con colores diferenciados (Pendiente=amarillo, En progreso=azul, Resuelta=verde, Cancelada=gris)
- [x] Error de carga como Toast (no crash)
- [x] Link "Nueva Tarea" → `/coordinacion/tareas/nuevo`
- [x] Link "Ver" por fila → `/coordinacion/tareas/{id}`
- [x] Mensaje vacío si no hay tareas

## TareaDetailPage

- [x] Muestra: título, estado (con badge de color), asignado_a (nombre via usuariosById), asignado_por (nombre via usuariosById), created_at, updated_at
- [x] Botones para cambiar estado (muestra solo estados distintos al actual)
- [x] Toast al cambiar estado (éxito y error)
- [x] Sección de comentarios con lista + formulario de agregar
- [x] Link de vuelta a lista

## TareaFormPage

- [x] Campos: título (requerido), descripción (opcional), asignado_a (combobox de usuarios)
- [x] `useNavigate` importado y usado correctamente (era bug pre-existente)
- [x] Redirect a lista tras creación exitosa
- [x] Validación inline (título y asignado requeridos)
- [x] Toast de error en fallo

## ComentarioList

- [x] Usa `ComentarioResponse` con campo `texto` (no `contenido`)
- [x] Sin threading / sin `padre_id`
- [x] Prop `usuariosById?: Map<string, string>` para resolver nombre del autor
- [x] `created_at` formateado con `toLocaleString()`
- [x] Formulario de nuevo comentario integrado en la lista

## Criterios transversales

- [x] Identidad desde JWT (no URL/body)
- [x] Multi-tenancy: `tenant_id` manejado por el backend en cada endpoint
- [x] RBAC: permisos `tareas:ver` / `tareas:gestionar` (declarados en el backend)
- [x] Soft delete: no hay DELETE en el módulo (solo cambio de estado a Cancelada)
- [x] Auditoría: cambios de estado y comentarios auditados por el backend
- [x] Sin `any` en TypeScript
- [x] Componentes < 200 LOC
