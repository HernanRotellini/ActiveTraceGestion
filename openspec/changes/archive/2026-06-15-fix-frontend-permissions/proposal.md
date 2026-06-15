## Why

El frontend está recibiendo errores 403 en varias pantallas porque los permisos que utiliza (`calificaciones:ver`, `equipos:ver`, `avisos:ver`, `liquidaciones:ver`, etc.) no existen en el backend, o no están asignados a los roles correctos. Además, el frontend nunca propaga los permisos desde `/api/auth/me`, por lo que cualquier usuario no-ADMIN no puede acceder a ninguna pantalla protegida.

## What Changes

1. **Agregar permisos faltantes al backend** — crear los permisos que el frontend necesita y que no existen (`calificaciones:ver`, `avisos:ver`, `avisos:gestionar`, `equipos:ver`, `equipos:gestionar`, `encuentros:ver`, `coloquios:ver`, `tareas:ver`, `liquidaciones:ver`, `liquidaciones:gestionar`)
2. **Asignar permisos correctos a cada rol** — revisar la matriz rol-permiso para que cada rol tenga los permisos que realmente necesita para las pantallas que ve
3. **Sincronizar guards del backend** — actualizar `require_permission(...)` en los endpoints que usan nombres de permisos que ya no existen o que son incorrectos
4. **Corregir la propagación de permisos en el frontend** — el `GET /api/auth/me` debe devolver permisos, el tipo `MeResponse` debe incluirlos, y `useLogin`/`useChallenge2fa` deben propagarlos al `setSession()`
5. **Corregir nombres de permisos en rutas del frontend** — donde el frontend usaba nombres incorrectos, actualizar al nombre canónico

## Capabilities

### New Capabilities
- `autorizacion`: permisos RBAC — definición de permisos, asignación a roles, y verificación tanto en frontend como backend

### Modified Capabilities
<!-- No existing specs to modify — this is a cross-cutting fix -->

## Impact

- **Backend**: `backend/app/models/permisos.py` (nuevas constantes), migración Alembic (nuevos permisos + asignaciones), múltiples routers (corregir nombre de permiso en `require_permission`)
- **Frontend**: `frontend/src/features/auth/types.ts` (MeResponse), `frontend/src/features/auth/hooks/useLogin.ts`, `frontend/src/features/auth/hooks/useChallenge2fa.ts`, `frontend/src/routes/index.tsx` (PermissionGuard names)
- **Seed data**: actualizar `backend/scripts/seed_dev_data.py` si es necesario
