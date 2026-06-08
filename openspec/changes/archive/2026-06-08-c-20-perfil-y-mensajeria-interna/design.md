## Context

El sistema ya cuenta con:
- Modelo `Usuario` con campos base (nombre, apellidos, email, dni, cuil, cbu, alias_cbu, banco, facturador)
- CRUD admin de usuarios en `/api/admin/usuarios` con cifrado PII
- Auth JWT con `get_current_user` que resuelve identidad y tenant
- Endpoint `POST /api/v1/auth/logout` existente (C-03)
- Permiso `usuarios:gestionar` para administración

Lo que falta para perfil propio y mensajería interna (F11, F3.4):
1. Endpoints de perfil propio (cualquier usuario autenticado puede ver/editar sus datos)
2. Algunos campos nuevos en Usuario (regional, modalidad_cobro, genero, condicion_impositiva, matricula_profesional)
3. Modelos de mensajería interna: HiloMensaje + MensajeInterno
4. Endpoints de inbox para gestionar hilos

## Goals / Non-Goals

**Goals:**
- Exponer `GET /api/v1/perfil` y `PUT /api/v1/perfil` para que el usuario autenticado gestione sus datos
- Agregar campos de perfil faltantes al modelo Usuario (migración)
- Implementar mensajería interna entre usuarios con hilos y respuestas
- CUIL como campo de solo lectura en perfil (no modificable por el usuario)
- Tests de edición, CUIL no modificable, hilos de mensajes, aislamiento

**Non-Goals:**
- No se modifican permisos existentes (el perfil es propio, no requiere permiso especial)
- No se implementa notificación push/email al recibir mensaje interno
- No se implementa búsqueda global de usuarios (eso existe en `/api/admin/usuarios`)
- El logout ya existe (C-03) — no se modifica

## Decisions

### 1. Perfil propio sin nuevo modelo
- **Decisión**: Usar el modelo `Usuario` existente, agregar columnas nuevas vía migración
- **Rationale**: El perfil ES el usuario desde la perspectiva del dominio. No justifica un modelo separado `Perfil`. Los campos nuevos son extensiones naturales.
- **Alternativa**: Modelo `Perfil` separado con FK a Usuario → sobreingeniería para datos 1:1

### 2. Mensajería: HiloMensaje + MensajeInterno (dos tablas)
- **Decisión**: `HiloMensaje` (id, tenant_id, asunto, participantes_ids, created_at, updated_at, ultimo_mensaje_at) y `MensajeInterno` (id, hilo_id, remitente_id, cuerpo, created_at)
- **Rationale**: Separar el hilo (metadatos) de los mensajes (contenido) permite listar hilos sin cargar todos los mensajes. El hilo conoce sus participantes (array de UUIDs) para filtrar por usuario.
- **Alternativa**: Tabla única con todo → difícil de listar/paginar. Tres tablas (hilo, participante, mensaje) → más joins para un caso simple.

### 3. Participantes como array JSONB en HiloMensaje
- **Decisión**: Almacenar `participantes_ids` como JSONB array de UUIDs en HiloMensaje
- **Rationale**: La mensajería es 1:1 o 1:pocos (coordinador→docente). No requiere tabla de participantes separada. JSONB permite indexación GIN si es necesario.
- **Riesgo**: Para hilos grupales grandes (>100 participantes), la query de filtrado puede degradar. → Mitigación: en esta versión solo hay hilos 1:1 o 1:pocos.

### 4. Perfil sin permiso especial
- **Decisión**: Cualquier usuario autenticado puede ver/editar su propio perfil. No se requiere `require_permission`.
- **Rationale**: El perfil propio es un derecho del usuario, no un privilegio administrativo. La autorización se da por `get_current_user` (solo puede editar sus propios datos).
- **Seguridad**: El endpoint fuerza `usuario_id = current_user.user_id` — no se puede editar el perfil de otro.

### 5. Inbox sin permiso especial
- **Decisión**: Cualquier usuario autenticado puede ver sus hilos y mensajes. Para crear un hilo o responder, solo necesita estar autenticado.
- **Rationale**: La mensajería interna es entre usuarios registrados. El filtro es por `participantes_ids @> [current_user.user_id]`.

### 6. CUIL solo lectura
- **Decisión**: `PUT /perfil` rechaza explícitamente el campo `cuil` con 422 si se envía
- **Rationale**: El CUIL es gestionado por ADMIN. El usuario no debe poder modificarlo. Se valida en el schema Pydantic con `Field(frozen=True)` o se excluye del schema de escritura.

## Risks / Trade-offs

- **[Seguridad perfil]** Si el schema de escritura incluye campos que no deberían ser editables (como `estado` o `facturador`), un usuario podría auto-modificarlos. → Mitigación: schema de escritura explícito con solo los campos permitidos (DTO separado del modelo).
- **[Aislamiento inbox]** Los hilos se filtran por `tenant_id` (heredado de TenantScopedMixin) y por `participantes_ids`. Asegurar que un usuario de tenant A no vea hilos de tenant B. → Mitigación: `HiloMensaje` usa TenantScopedMixin con filtro automático.
- **[Escalabilidad mensajería]** Si el volumen de mensajes es alto (>10K por hilo), la paginación de mensajes puede ser lenta sin índice compuesto. → Mitigación: índice `(hilo_id, created_at)` en `mensajes_internos`.
