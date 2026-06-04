## Why

La Épica 3 (Comunicación con Alumnos) es el brazo ejecutor del core del producto: detectar atrasados y comunicarse con ellos. Hasta C-11 el sistema detecta alumnos atrasados (F2.2) pero no puede actuar sobre esa información. Sin C-12 el producto termina en diagnóstico — con C-12 cierra el loop detectar → comunicar. Además, la cola asíncrona con aprobación humana (F3.3) es un diferenciador frente a soluciones que envían sin control.

## What Changes

- Nuevo modelo `Comunicacion` con máquina de estados (RN-15), cifrado AES-256 en `destinatario`, soft delete, agrupación por `lote_id`
- Worker asíncrono en `backend/workers/comunicaciones_worker.py` que consume Pendiente → Enviando → Enviado/Error
- Preview obligatorio (RN-16): `POST /api/comunicaciones/preview` con sustitución de variables
- Envío masivo con cola (F3.2): `POST /api/comunicaciones/enviar` encola un Comunicacion por alumno atrasado
- Aprobación humana configurable por tenant (RN-17): endpoints para aprobar/cancelar lotes o mensajes individuales
- Permisos: `comunicacion:enviar`, `comunicacion:aprobar`
- Audit actions: `COMUNICACION_ENVIAR`, `COMUNICACION_APROBAR`, `COMUNICACION_CANCELAR`
- El envío real es un stub/simulación (el delivery SMTP/API vendrá en change posterior)
- Migración Alembic

## Capabilities

### New Capabilities
- `comunicaciones`: modelo Comunicacion, máquina de estados, preview, envío masivo con cola, aprobación humana, worker asíncrono, cifrado de destinatario

### Modified Capabilities
<!-- No existing specs change behavior—this is entirely new -->

## Impact

- **Modelo**: nuevo `Comunicacion` en SQLAlchemy; nuevo enum `EstadoComunicacion`; migración Alembic
- **Services**: `ComunicacionService` con lógica de preview, encolado, aprobación, cancelación; `ComunicacionWorker` asíncrono
- **Repositories**: `ComunicacionRepository` (scope tenant, filtros por lote, estado)
- **API**: 7 nuevos endpoints bajo `/api/comunicaciones/` con guards `comunicacion:enviar` y `comunicacion:aprobar`
- **Workers**: nuevo módulo `backend/workers/comunicaciones_worker.py`
- **Config**: flag `aprobacion_comunicaciones_obligatoria` en configuración del tenant
- **Encryption**: helper AES-256 existente se reutiliza para cifrar `destinatario`
- **Dependencias**: C-11 (analisis-atrasados-reportes) — consume endpoint de atrasados para saber a quiénes enviar
