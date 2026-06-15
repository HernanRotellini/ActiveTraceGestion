## Context

El sistema RBAC tiene **3 capas de permisos** que están desincronizadas:

1. **Backend — constantes y seed**: 23 permisos definidos en `permisos.py`, seedeados en migración `20260602_0003`
2. **Backend — guards en endpoints**: `require_permission(...)` en routers con esos 23 permisos
3. **Frontend — PermissionGuard en rutas**: 16 permisos, de los cuales solo **5 coinciden** con el backend

### Mapa de discrepancias

| Frontend espera | Backend tiene | Estado |
|---|---|---|
| `calificaciones:ver` | `calificaciones:importar` | ❌ No existe |
| `atrasados:ver` | `atrasados:ver` | ✅ Ok |
| `comunicacion:enviar` | `comunicacion:enviar` | ✅ Ok |
| `equipos:ver` | `equipos:asignar` | ❌ No existe |
| `equipos:gestionar` | `equipos:asignar` | ❌ No existe |
| `avisos:ver` | `avisos:publicar` | ❌ No existe |
| `avisos:gestionar` | `avisos:publicar` | ❌ No existe |
| `tareas:ver` | `tareas:gestionar` | ❌ No existe |
| `tareas:gestionar` | `tareas:gestionar` | ✅ Ok |
| `encuentros:ver` | `encuentros:gestionar` | ❌ No existe |
| `coloquios:ver` | `coloquios:gestionar` | ❌ No existe |
| `estructura:gestionar` | `estructura:gestionar` | ✅ Ok |
| `liquidaciones:ver` | (solo `operar_grilla` y `calcular_cerrar`) | ❌ No existe |
| `liquidaciones:gestionar` | (solo `operar_grilla`) | ❌ No existe |
| `usuarios:gestionar` | `usuarios:gestionar` | ✅ Ok |
| `auditoria:ver` | `auditoria:ver` | ✅ Ok |

Además:
- El `/api/auth/me` **nunca devuelve permisos**, y el frontend nunca los propaga
- ADMIN no tiene asignados permisos de liquidaciones ni facturas (solo FINANZAS tiene)

## Goals / Non-Goals

**Goals:**
- ADMIN puede ver todas las pantallas sin 403
- Roles no-ADMIN ven solo sus pantallas (granularidad correcta)
- El frontend recibe y propaga los permisos correctamente
- Los nombres de permisos son consistentes entre frontend y backend

**Non-Goals:**
- No se rediseña la UI del sidebar
- No se agregan nuevas funcionalidades
- No se cambia la lógica de alcance (`propio`/`global`)

## Decisions

### D1: Agregar permisos "view" al backend

Se agregan 9 permisos nuevos que el frontend ya usa:

| Nuevo permiso | Descripción |
|---|---|
| `calificaciones:ver` | Ver calificaciones |
| `equipos:ver` | Ver equipos docentes |
| `equipos:gestionar` | Crear/editar equipos docentes |
| `avisos:ver` | Ver avisos |
| `avisos:gestionar` | Crear/editar avisos |
| `tareas:ver` | Ver tareas internas |
| `encuentros:ver` | Ver encuentros |
| `coloquios:ver` | Ver coloquios |
| `liquidaciones:ver` | Ver liquidaciones, historial y facturas |

Total: 23 + 9 = **32 permisos**.

### D2: Separar guards en endpoints GET vs POST/PUT/DELETE

Los endpoints de solo lectura (`GET`) usan el permiso `:ver`, los de escritura (`POST/PUT/DELETE`) usan el permiso `:gestionar` o el específico existente.

### D3: `/api/auth/me` devuelve permisos del usuario

El endpoint `/auth/me` ahora incluye `permissions: list[str]` en su respuesta calculado por `AuthorizationService.effective_permissions()`. Así el frontend recibe los permisos en el login.

### D4: ADMIN recibe todos los permisos operativos

Se agregan al rol ADMIN: `liquidaciones:operar_grilla`, `liquidaciones:calcular_cerrar`, `facturas:gestionar`. Así ADMIN ve liquidaciones y facturas.

### D5: El frontend propaga permisos desde `/auth/me`

Se corrigen:
- `MeResponse` → agrega `permissions: string[]`
- `useLogin.ts` → pasa `permissions: me.permissions` al `setSession()`
- `useChallenge2fa.ts` → igual

## Mapa de cambios por router

### `calificaciones.py`
- `GET /api/calificaciones` → cambia de `calificaciones:importar` a `calificaciones:ver`
- POST/import endpoints → se quedan con `calificaciones:importar`

### `avisos.py`
- `GET /api/admin/avisos`, `GET .../{id}`, `GET .../{id}/stats` → `avisos:ver`
- `POST`, `PUT`, `DELETE` → `avisos:gestionar`

### `equipos.py`
- `GET /api/equipos/exportar` → `equipos:ver` (reemplaza `equipos:asignar`)
- `POST`, `PATCH` → `equipos:gestionar` (reemplaza `equipos:asignar`)

### `encuentros.py`
- `GET` endpoints → `encuentros:ver`
- `POST`, `PATCH` → `encuentros:gestionar`

### `coloquios.py`
- `GET /api/coloquios`, `GET /.../{id}`, `GET /.../turnos`, `GET /.../resultados`, `GET /admin/agenda` → `coloquios:ver`
- `POST`, `DELETE`, import → `coloquios:gestionar`

### `tareas.py`
- `GET /api/tareas/mis`, `GET /api/tareas`, `GET /.../{id}` → `tareas:ver`
- `POST`, `PATCH`, `POST .../delegar`, `POST .../comentarios` → `tareas:gestionar`

### `liquidaciones.py`
- `GET /api/liquidaciones`, `GET .../{id}` → `liquidaciones:ver`
- `POST /api/liquidaciones/preview`, `POST .../cerrar` → `liquidaciones:gestionar`
- Grilla se queda con `liquidaciones:operar_grilla`

### `facturas.py`
- `GET /api/facturas`, `GET .../{id}` → `liquidaciones:ver`
- `POST`, `PUT`, `DELETE`, `POST .../abonada` → `facturas:gestionar`

## Diagrama de flujo de permisos (post-fix)

```
Login → POST /auth/login → JWT (roles en claims)
  → GET /auth/me → { user_id, tenant_id, roles, permissions: [...] }
  → Frontend propaga a session.user.permissions

Protected route → PermissionGuard → hasPermission("X:Y")
  → Si ADMIN → true (bypass)
  → Si no → check en session.user.permissions.includes("X:Y")

API call → require_permission("X:Y") → AuthorizationService
  → DB: roles → roles_permisos → permisos
  → 403 si no está en el set
```

### D6: Mostrar nombre legible del usuario en lugar de UUID

El layout principal (`MainLayout`) muestra en la esquina inferior izquierda el `user_id` (UUID). Se reemplaza por el nombre del usuario (de la tabla `usuarios`). Para eso:

- El endpoint `/api/auth/me` debe devolver también `nombre` y `apellidos` del usuario
- O bien el JWT debe contener esos datos
- O el frontend debe consultar `GET /api/auth/me` que ya devuelve el email

Decisión: agregar `nombre` y `apellidos` al `CurrentUserResponse` en `/auth/me`, consultando desde `Usuario` model. Así el frontend lo recibe al login sin calls extra.

### D7: Sidebar filtra herramientas por permiso real

El sidebar ya filtra por `hasPermission()`. Al corregir la propagación de permisos (D5), el filtrado empieza a funcionar correctamente para no-ADMIN. No requiere cambios adicionales.

## Verificación por rol post-implementación

Para cada rol se verificará que:

| Rol | Pantallas visibles | Pantallas ocultas |
|---|---|---|
| ADMIN | Todas | Ninguna |
| COORDINADOR | Equipos, Avisos, Tareas, Encuentros, Coloquios, Setup, Monitor Gral, Comisiones, Entregas, Comunicaciones | Liquidaciones, Facturas, Admin usuarios, Admin estructura, Auditoría |
| PROFESOR | Comisiones, Entregas, Comunicaciones, Monitor | Equipos, Avisos, Tareas, Encuentros, Coloquios, Setup, Liquidaciones, Admin |
| TUTOR | Entregas, Monitor | Comisiones, Comunicaciones, Equipos, Avisos, etc. |
| FINANZAS | Liquidaciones, Grilla, Facturas, Auditoría | Comisiones, Equipos, Avisos, Admin estructura, etc. |
| NEXO | Solo avisos (confirmar) | Todo lo demás |

## Risks / Trade-offs

- **[Riesgo] Que un GET quede sin el permiso correcto** → Mitigación: verificar cada endpoint contra la tabla de decisión D2
- **[Riesgo] Que el seed de permisos duplique asignaciones al correr de nuevo** → Mitigación: migración nueva (no modificar la existente) con `checkfirst` en los inserts
- **[Trade-off] Agregar permisos nuevos** vs reusar los existentes → Decidimos agregar porque la semántica "ver" vs "gestionar" es correcta y el frontend ya la diseñó así
