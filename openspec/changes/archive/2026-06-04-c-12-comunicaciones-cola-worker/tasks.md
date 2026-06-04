## 1. Modelo de datos y migración

- [x] 1.1 Crear enum `EstadoComunicacion` (Pendiente, Enviando, Enviado, Error, Cancelado) en `backend/models/comunicacion.py`
- [x] 1.2 Crear modelo `Comunicacion` en `backend/models/comunicacion.py` con todos los campos, soft delete y relaciones
- [x] 1.3 Implementar máquina de estados con validación de transiciones (RN-15)
- [x] 1.4 Crear migración Alembic para tabla `comunicaciones`
- [x] 1.5 Crear schemas Pydantic en `backend/schemas/comunicacion.py` con `extra='forbid'`

## 2. Cifrado de destinatario

- [x] 2.1 Integrar helper AES-256 existente (`app.core.encryption`) para cifrar/descifrar `destinatario` en el service
- [x] 2.2 Asegurar que logs no expongan el destinatario en texto plano (fallback a `[cifrado]` en error)

## 3. Repository

- [x] 3.1 Crear `ComunicacionRepository` en `backend/repositories/comunicacion_repository.py` con scope de tenant por defecto
- [x] 3.2 Implementar métodos: crear, listar_lotes, detalle_lote, pendientes_para_procesar, transicionar_estado

## 4. Service layer

- [x] 4.1 Crear `ComunicacionService` en `backend/services/comunicacion_service.py`
- [x] 4.2 Implementar `preview(asunto, cuerpo, variables)` con sustitución de `{{nombre}}`, `{{materia}}`, `{{comision}}`
- [x] 4.3 Implementar `enviar_masivo(materia_id, asunto, cuerpo)` que consulta atrasados (C-11) y encola Comunicaciones
- [x] 4.4 Implementar `aprobar_lote(lote_id)` que transiciona Pendiente→Enviando (RN-17)
- [x] 4.5 Implementar `cancelar_lote(lote_id)` y `cancelar_comunicacion(id)` que transicionan Pendiente→Cancelado
- [x] 4.6 Integrar audit log en envío, aprobación y cancelación

## 5. API Routes

- [x] 5.1 Crear `backend/app/api/v1/routers/comunicaciones.py` con FastAPI router y guards de permisos
- [x] 5.2 Implementar `POST /api/comunicaciones/preview` (guard: `comunicacion:enviar`)
- [x] 5.3 Implementar `POST /api/comunicaciones/enviar` (guard: `comunicacion:enviar`)
- [x] 5.4 Implementar `GET /api/comunicaciones/lotes` (guard: `comunicacion:enviar`)
- [x] 5.5 Implementar `GET /api/comunicaciones/lotes/{lote_id}` (guard: `comunicacion:enviar`)
- [x] 5.6 Implementar `POST /api/comunicaciones/lotes/{lote_id}/aprobar` (guard: `comunicacion:aprobar`)
- [x] 5.7 Implementar `POST /api/comunicaciones/lotes/{lote_id}/cancelar` (guard: `comunicacion:aprobar`)
- [x] 5.8 Implementar `POST /api/comunicaciones/{id}/cancelar` (guard: `comunicacion:aprobar`)
- [x] 5.9 Registrar router en la aplicación FastAPI

## 6. Permisos y auditoría

- [x] 6.1 Seeds ya existen en migración `20260602_0003` (comunicacion:enviar, comunicacion:aprobar ya estaban en la matriz RBAC)
- [x] 6.2 Agregar audit actions `COMUNICACION_ENVIAR`, `COMUNICACION_APROBAR`, `COMUNICACION_CANCELAR`

## 7. Worker asíncrono de despacho

- [x] 7.1 Crear `backend/app/workers/stubs.py` con `simular_envio()` (éxito 95%, error 5%)
- [x] 7.2 Crear `backend/app/workers/comunicaciones_worker.py` con bucle asyncio de polling
- [x] 7.3 Implementar lógica: consultar Pendientes, transicionar a Enviando, ejecutar stub, transicionar a Enviado/Error
- [x] 7.4 Respetar flag `aprobacion_comunicaciones_obligatoria` (no procesar lotes no aprobados)
- [x] 7.5 Agregar configuración de intervalo de polling y rate de éxito vía settings

## 8. Configuración por tenant

- [x] 8.1 Agregar campo `settings` JSONB en modelo Tenant
- [x] 8.2 Implementar helper `aprobacion_requerida()` en el service para leer flag desde tenant settings
- [x] 8.3 Crear migración para agregar campo settings a Tenant

## 9. Tests

- [x] 9.1 Tests de máquina de estados: transiciones válidas e inválidas (RN-15)
- [x] 9.2 Tests de preview con sustitución de variables (RN-16)
- [x] 9.3 Tests de envío masivo: con atrasados, sin atrasados, con aprobación obligatoria
- [x] 9.4 Tests de aprobación de lote completo e individual
- [x] 9.5 Tests de cancelación de lote e individual
- [x] 9.6 Tests de cifrado/descifrado de destinatario
- [x] 9.7 Tests de worker: procesa Pendiente→Enviado, salta no aprobados, registra Error
- [x] 9.8 Tests de autorización: 403 sin permiso, 401 sin auth
- [x] 9.9 Tests de tenant isolation
