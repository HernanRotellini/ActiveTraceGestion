## Why

Actualmente el sistema no permite que los usuarios (docentes, coordinadores, etc.) actualicen sus propios datos de perfil — nombre, datos bancarios, regional, modalidad de cobro — ni accedan a una bandeja de mensajería interna entre usuarios registrados. Los usuarios dependen del ADMIN para cualquier cambio de datos personales, y la comunicación entre roles del sistema (coordinador→docente, etc.) no tiene un canal interno: todo deriva en comunicaciones externas (email). Esto genera fricción operativa y pérdida de trazabilidad en las comunicaciones internas.

## What Changes

- Endpoints CRUD de **perfil propio** (`/api/v1/perfil`):
  - `GET /perfil` — ver datos propios
  - `PUT /perfil` — actualizar campos editables (nombre, banco, CBU, alias, regional, modalidad_cobro, etc.)
  - CUIL es solo lectura
- Nuevo modelos `HiloMensaje` y `MensajeInterno` para **mensajería interna** entre usuarios registrados
  - Migración Alembic para tablas `hilos_mensajes` y `mensajes_internos`
- Endpoints de inbox (`/api/v1/inbox`):
  - `GET /inbox` — listar hilos activos del usuario
  - `GET /inbox/{id}` — ver hilo con mensajes
  - `POST /inbox/{id}/responder` — responder en un hilo
  - `POST /inbox` — iniciar nuevo hilo con otro usuario
- Logout explícito (`POST /api/v1/auth/logout`) — reusa C-03, ya existe
- Tests completos de perfil (edición, CUIL no modificable) e inbox (hilos, responder, aislamiento)

## Capabilities

### New Capabilities
- `perfil-propio`: Gestión de perfil de usuario autenticado (lectura + edición de campos permitidos)
- `mensajeria-interna`: Bandeja de mensajes entre usuarios registrados del sistema (hilos, responder)

### Modified Capabilities
- `usuarios`: Se agregan campos de perfil al modelo Usuario (regional, modalidad_cobro, genero, condicion_impositiva, matricula_profesional)

## Impact

- **Modelos**: Se agregan campos a `Usuario` existente. Nuevos modelos `HiloMensaje` y `MensajeInterno`
- **Migración**: Nueva migración Alembic para columnas de perfil + tablas de mensajería
- **API**: Nuevos routers `perfil.py` e `inbox.py` en `/api/v1/`
- **Services**: `perfil_service.py` e `inbox_service.py`
- **Repositories**: `inbox_repository.py`
- **Permisos**: No requiere nuevos permisos — el perfil es propio, el inbox es propio. Cualquier usuario autenticado accede
- **Tests**: `test_c20_perfil.py` y `test_c20_inbox.py`
