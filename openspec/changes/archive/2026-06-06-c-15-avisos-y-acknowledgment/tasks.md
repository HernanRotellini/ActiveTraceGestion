## 1. Modelos y Migración

- [x] 1.1 Crear modelo `Aviso` en `backend/app/models/aviso.py` con campos: id, tenant_id, alcance (enum: Global/PorMateria/PorCohorte/PorRol), materia_id (nullable FK), cohorte_id (nullable FK), rol_destino (nullable), severidad (enum: Info/Advertencia/Crítico), titulo, cuerpo, inicio_en, fin_en (nullable), orden (default 0), activo (default true), requiere_ack (default false), timestamps (mixin C-02), soft delete
- [x] 1.2 Crear modelo `AcknowledgmentAviso` en el mismo archivo con: id, tenant_id, aviso_id (FK), usuario_id (FK), confirmado_at. Unique constraint (aviso_id, usuario_id)
- [x] 1.3 Registrar ambos modelos en `backend/app/models/__init__.py`
- [x] 1.4 Crear migración Alembic `20260606_0011_avisos_acknowledgment.py` con tabla `aviso` y `acknowledgment_aviso`, incluyendo índices compuestos para filtrado por visibilidad

## 2. Schemas Pydantic

- [x] 2.1 Crear `backend/app/schemas/aviso.py` con:
  - `AvisoCreate`: todos los campos de creación con validación condicional (materia_id requerido si alcance=PorMateria, etc.), `extra='forbid'`
  - `AvisoUpdate`: mismos campos opcionales
  - `AvisoResponse`: todos los campos incluyendo id, timestamps
  - `AvisoListResponse`: versión resumida para listados
  - `AckCreate`: sin cuerpo (solo aviso_id de path)
  - `AckResponse`: id, aviso_id, confirmado_at
  - `AvisoStatsResponse`: total_acks, usuarios_sin_confirmar
- [x] 2.2 Registrar schemas en `backend/app/schemas/__init__.py`

## 3. Repositorio

- [x] 3.1 Crear `backend/app/repositories/aviso_repository.py` con:
  - `listar_visibles(tenant_id, roles, materia_ids, cohorte_ids)` — query con filtros de alcance según diseño
  - `listar_admin(tenant_id, filtros)` — listado admin con filtros opcionales
  - `obtener_por_id(id)` — con scope de tenant
  - `crear(datos)` — insert
  - `actualizar(id, datos)` — update
  - `desactivar(id)` — soft delete (activo=false)
  - `obtener_stats(aviso_id)` — COUNT de acks + usuarios sin confirmar
- [x] 3.2 Crear `backend/app/repositories/acknowledgment_repository.py` con:
  - `confirmar(aviso_id, usuario_id)` — insert con ON CONFLICT DO NOTHING (idempotente)
  - `obtener_por_aviso_y_usuario(aviso_id, usuario_id)` — para verificar si ya confirmó
  - `contar_por_aviso(aviso_id)` — COUNT
  - `listar_avisos_pendientes_ack(tenant_id, usuario_id, roles, materia_ids, cohorte_ids)` — avisos visibles con requiere_ack=true y sin ack del usuario
- [x] 3.3 Registrar ambos repositorios en `backend/app/repositories/__init__.py`

## 4. Servicio

- [x] 4.1 Crear `backend/app/services/aviso_service.py` con:
  - `listar_visibles(usuario, roles, materias_ids, cohortes_ids)` → delegate al repository
  - `listar_admin(tenant_id, filtros)` → delegate al repository con filtros
  - `crear(tenant_id, datos, actor_id)` → validar, crear aviso, audit log
  - `actualizar(aviso_id, tenant_id, datos, actor_id)` → validar pertenencia, actualizar, audit log
  - `desactivar(aviso_id, tenant_id, actor_id)` → soft delete, audit log
  - `confirmar_lectura(aviso_id, usuario_id, tenant_id)` → idempotente, audit log
  - `listar_pendientes_ack(usuario, roles, materias_ids, cohortes_ids)` → filtrar visibles + sin ack
  - `obtener_stats(aviso_id, tenant_id)` → contadores derivados
- [x] 4.2 Registrar servicio en `backend/app/services/__init__.py`

## 5. Router API

- [x] 5.1 Crear `backend/app/api/v1/routers/avisos.py` con:
  - `GET /api/avisos` — listar visibles (autenticado)
  - `GET /api/avisos/pendientes-ack` — listar pendientes de confirmación (autenticado)
  - `POST /api/avisos/{id}/ack` — confirmar lectura (autenticado, idempotente)
  - `GET /api/admin/avisos` — listar todos (permiso `avisos:publicar`)
  - `POST /api/admin/avisos` — crear aviso (permiso `avisos:publicar`)
  - `GET /api/admin/avisos/{id}` — detalle (permiso `avisos:publicar`)
  - `PUT /api/admin/avisos/{id}` — actualizar (permiso `avisos:publicar`)
  - `DELETE /api/admin/avisos/{id}` — desactivar (permiso `avisos:publicar`)
  - `GET /api/admin/avisos/{id}/stats` — estadísticas (permiso `avisos:publicar`)
- [x] 5.2 Registrar router en `backend/app/api/v1/routers/__init__.py`
- [x] 5.3 Incluir router en `backend/app/main.py` (debajo de los routers existentes)

## 6. Permisos RBAC

- [x] 6.1 Agregar permiso `avisos:publicar` al seed de roles (COORDINADOR, ADMIN) en el módulo de RBAC
- [x] 6.2 Si existe un seed script o migración de permisos, agregar el nuevo permiso allí

## 7. Tests

- [x] 7.1 Crear `backend/tests/test_avisos.py` con tests para:
  - **Modelo**: creación de aviso, creación de ack, unique constraint (aviso_id, usuario_id)
  - **Visibilidad**: aviso Global visible para todos, PorRol visible solo para el rol destino, PorMateria visible solo para usuarios de esa materia, PorCohorte visible solo para usuarios de esa cohorte
  - **Vigencia**: aviso fuera de vigencia (fin_en pasado) no se muestra, aviso futuro (inicio_en futuro) no se muestra
  - **Ack**: confirmación exitosa, confirmación idempotente, aviso con requiere_ack aparece en pendientes hasta confirmar
  - **Admin CRUD**: creación, actualización, desactivación (soft delete), listado admin incluye inactivos
  - **Permisos**: usuario sin `avisos:publicar` recibe 403 en endpoints admin
  - **Aislamiento tenant**: avisos de tenant A no visibles en tenant B
  - **Auditoría**: creación de aviso genera audit log
  - **Orden**: avisos ordenados por orden ASC e inicio_en DESC
  - **Stats**: total_acks refleja confirmaciones, usuarios_sin_confirmar listados

## 8. Sync spec canónico

- [x] 8.1 Copiar spec delta a `openspec/specs/avisos-gestion/spec.md` como spec canónico del módulo
