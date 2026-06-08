## 1. Migration — Profile columns + messaging tables

- [x] 1.1 Create Alembic migration adding columns to `usuarios`: `regional`, `modalidad_cobro`, `genero`, `condicion_impositiva`, `matricula_profesional`
- [x] 1.2 Create table `hilos_mensajes` (HiloMensaje): id, tenant_id, asunto, participantes_ids (JSONB), ultimo_mensaje_at, created_at, updated_at, deleted_at
- [x] 1.3 Create table `mensajes_internos` (MensajeInterno): id, hilo_id, remitente_id, cuerpo, created_at
- [x] 1.4 Add indexes: `(hilo_id, created_at)` on mensajes_internos, GIN index on hilos_mensajes.participantes_ids

## 2. Models

- [x] 2.1 Add new profile columns to `Usuario` model in `usuarios_asignaciones.py`
- [x] 2.2 Create `HiloMensaje` model in new `hilo_mensaje.py` with TenantScopedMixin
- [x] 2.3 Create `MensajeInterno` model in `mensaje_interno.py`
- [x] 2.4 Register new models in `models/__init__.py`

## 3. Schemas

- [x] 3.1 Create `schemas/perfil.py`: `PerfilResponse` (all fields, PII decrypted), `PerfilUpdate` (only editable fields, no cuil)
- [x] 3.2 Create `schemas/inbox.py`: `HiloResponse`, `HiloListResponse`, `MensajeResponse`, `CrearHiloRequest`, `ResponderRequest`
- [x] 3.3 All schemas with `extra='forbid'` and `from_attributes=True`

## 4. Profile route + service

- [x] 4.1 Create `services/perfil_service.py`: `get_perfil()`, `update_perfil()` — validar CUIL no modificable, cifrar PII al guardar
- [x] 4.2 Create `routers/perfil.py`: `GET /api/v1/perfil`, `PUT /api/v1/perfil` (sin require_permission — es propio)
- [x] 4.3 Register router in `main.py`

## 5. Inbox route + service + repository

- [x] 5.1 Create `repositories/inbox_repository.py`: list hilos by participant, get hilo by id, create hilo, create mensaje
- [x] 5.2 Create `services/inbox_service.py`: list threads, view thread, reply, create new thread — verificar participante
- [x] 5.3 Create `routers/inbox.py`: `GET /inbox`, `GET /inbox/{id}`, `POST /inbox/{id}/responder`, `POST /inbox`
- [x] 5.4 Register router in `main.py`
- [x] 5.5 Add `get_inbox_service` dependency in `core/dependencies.py`

## 6. Tests

- [x] 6.1 Create `tests/test_c20_perfil.py`: get profile, update editable fields, CUIL rejected (422), partial update, email uniqueness
- [x] 6.2 Create `tests/test_c20_inbox.py`: list empty inbox, create thread, view thread, reply, non-participant 404, tenant isolation
