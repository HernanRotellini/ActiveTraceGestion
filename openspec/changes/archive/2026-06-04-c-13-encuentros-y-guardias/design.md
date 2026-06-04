## Context

El módulo de encuentros y guardias completa la trazabilidad de actividades sincrónicas (clases virtuales) y tutoriales (guardias de atención) en la plataforma. Actualmente no existe registro formal de estas actividades, lo que impide la supervisión por parte de COORDINADORES y la auditoría necesaria para liquidaciones de honorarios.

El diseño sigue los mismos patrones que el módulo de coloquios (`backend/app/services/coloquio_service.py`, `backend/app/repositories/coloquio_repository.py`, `backend/app/api/v1/routers/coloquios.py`): Services con inyección de session + tenant_id + usuario_id, repositorios tenant-scoped, routers con `require_permission`.

Los permisos `encuentros:gestionar` y `guardias:registrar` ya existen en `backend/app/models/permisos.py`.

## Goals / Non-Goals

**Goals:**
- Modelar SlotEncuentro como plantilla de recurrencia semanal (día_semana, hora, fecha_inicio, cant_semanas)
- Generar N instancias de InstanciaEncuentro al crear un SlotEncuentro (fecha = fecha_inicio + 7*i)
- Soportar encuentros únicos (InstanciaEncuentro sin slot asociado)
- Permitir edición individual de cada instancia (estado, meet_url, video_url, comentario) sin cascada al slot ni otras instancias (RN-14)
- Generar bloque HTML con los encuentros de una materia para publicación en LMS
- Vista admin transversal de todos los encuentros del tenant con filtros
- Modelar Guardia como entidad independiente asociada a Asignacion + materia + carrera + cohorte
- CRUD de guardias con consulta filtrada y exportación CSV
- Endpoints REST scoped por permiso `encuentros:gestionar` / `guardias:registrar`
- Migración Alembic para las tres tablas

**Non-Goals:**
- No se integra con calendarios externos (Google Calendar, Outlook)
- No se genera videoconferencia automáticamente (solo se almacena la URL provista)
- No hay notificaciones automáticas al crear/modificar encuentros
- No hay lógica de choque de horarios ni validación contra otras actividades
- Las guardias no se relacionan con liquidaciones de honorarios en este change

## Decisions

- **SlotEncuentro con dos modos excluyentes (RN-13)**: `cant_semanas > 0` activa modo recurrente (genera instancias). `cant_semanas = 0` + `fecha_unica` activa modo único (no genera instancias automáticas, la instancia se crea manualmente). Se valida que exactamente un modo esté activo.
- **Generación bulk de instancias**: al crear SlotEncuentro con `cant_semanas > 0`, el service calcula las fechas y hace un `session.add_all(instancias)` en una transacción. No hay lazy generation ni background job — las N instancias existen desde el momento de creación del slot. Esto simplifica consultas y evita estado inconsistente.
- **InstanciaEncuentro independiente del slot**: `slot_id` nullable + sin cascade de modificaciones. Cada instancia tiene su propio `estado`, `meet_url`, `video_url`, `comentario`. Modificar una instancia no toca el slot ni hermanas (RN-14).
- **Un repositorio para encuentros**: `EncuentroRepository` maneja SlotEncuentro e InstanciaEncuentro, siguiendo el patrón de repositorio tenant-scoped existente.
- **Guardia como modelo separado**: no hereda de SlotEncuentro ni InstanciaEncuentro. Guardia se relaciona con Asignacion (tutor + materia), no con encuentros. Tiene su propio repositorio y service. El permiso `guardias:registrar` controla escritura; `encuentros:gestionar` controla consulta global.
- **HTML block (F6.4)**: función utilitaria que recibe lista de instancias y renderiza un string HTML con una tabla básica. Sin dependencias externas (Jinja2 no es necesario para este template mínimo).
- **CSV export**: endpoint que serializa guardias a CSV con `StreamingResponse` y header `Content-Disposition: attachment`.
- **Permisos**: `encuentros:gestionar` para CRUD de slots e instancias (PROFESOR, COORDINADOR, ADMIN). `guardias:registrar` para que TUTOR registre sus propias guardias y COORDINADOR/ADMIN consulten globalmente.

## Risks / Trade-offs

- **[Riesgo] Generación bulk de instancias**: al crear un slot con 30 semanas, se generan 30 filas de una vez. Si se edita el slot (cambiar fecha_inicio o cant_semanas), las instancias existentes quedarían desfasadas. **Mitigación**: no se permite editar `fecha_inicio` ni `cant_semanas` de un slot existente — solo se puede dar de baja el slot (soft delete) y crear uno nuevo. Esto simplifica la lógica y evita estado inconsistente.
- **[Riesgo] HTML block inline**: el renderizado con string building es frágil si el formato crece. **Mitigación**: se limita a una tabla simple y se extrae a función utilitaria aislada, fácil de reemplazar por un template engine si el requerimiento escala.
- **[Trade-off] Guardia sin relación con liquidaciones**: las guardias alimentarán liquidaciones en C-18, pero por ahora son independientes. El diseño actual ya incluye los campos `asignacion_id`, `materia_id`, `carrera_id`, `cohorte_id` necesarios para la futura integración.
