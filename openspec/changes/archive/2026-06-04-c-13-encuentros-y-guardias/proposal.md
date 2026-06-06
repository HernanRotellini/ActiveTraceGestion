## Why

Los encuentros sincrónicos (clases virtuales) y las guardias de atención tutorial son actividades esenciales en la gestión académica, pero actualmente no hay registro formal de su planificación, ejecución ni auditoría. Sin este módulo, no existe trazabilidad sobre qué encuentros se realizaron, cuáles se cancelaron, qué grabaciones están disponibles, ni qué guardias cubrió cada tutor. Esto afecta la supervisión de COORDINADORES y la liquidación de honorarios docentes.

## What Changes

- Nuevos modelos: `SlotEncuentro` (plantilla de recurrencia), `InstanciaEncuentro` (encuentro concreto), `Guardia` (registro de guardia tutorial)
- Creación de encuentro recurrente: dado un slot semanal con fecha_inicio + cant_semanas, el sistema genera N instancias automáticamente
- Creación de encuentro único: instancia individual sin slot asociado
- Edición de instancia: estado (programado/realizado/cancelado), meet_url, video_url, comentario — sin afectar al slot ni otras instancias
- Generación de bloque HTML para publicar en el aula virtual del LMS
- Vista admin transversal de todos los encuentros del tenant (COORDINADOR/ADMIN)
- Registro de guardias asociadas a una Asignacion (tutor/docente + materia + carrera/cohorte)
- Consulta global y exportación CSV de guardias
- Endpoints REST: `/api/v1/encuentros/*`, `/api/v1/guardias/*` con permiso `encuentros:gestionar`
- Migración Alembic para las tres tablas
- Seed del permiso `encuentros:gestionar` para TUTOR, PROFESOR, COORDINADOR, ADMIN

## Capabilities

### New Capabilities
- `encuentros-gestion`: Gestión de slots e instancias de encuentro sincrónico (creación recurrente y única, edición de instancias, generación de HTML para LMS, vista admin transversal)
- `guardias-registro`: Registro, consulta y exportación de guardias tutoriales

### Modified Capabilities
<!-- No existing specs change behavior — purely additive -->

## Impact

- `backend/app/models/`: nuevos modelos `slot_encuentro.py`, `instancia_encuentro.py`, `guardia.py`
- `backend/app/repositories/`: nuevos repositorios con filtros por tenant y materia
- `backend/app/services/`: nuevo servicio con lógica de generación de instancias y renderizado HTML
- `backend/app/api/v1/routers/`: nuevos routers con dependencia `require_permission("encuentros:gestionar")`
- `backend/app/schemas/`: nuevos Pydantic schemas request/response
- `backend/app/models/permisos.py`: agregar constante `ENCUENTROS_GESTIONAR`
- `backend/app/seed/`: agregar asignación del permiso a roles TUTOR, PROFESOR, COORDINADOR, ADMIN
- Migración Alembic: crear tablas `slot_encuentro`, `instancia_encuentro`, `guardia`
