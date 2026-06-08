## Why

El backend de activia-trace está completo (20 changes, auth, RBAC, dominio académico). No existe aún una interfaz de usuario. Este change crea el shell de la SPA frontend y las pantallas de autenticación, que son el punto de entrada obligatorio para cualquier usuario del sistema. Sin este change no puede construirse ninguna feature de frontend (C-22, C-23, C-24).

## What Changes

- Scaffolding del proyecto frontend: React 18 + TypeScript + Vite con estructura feature-based
- Configuración e integración de dependencias: Tailwind CSS, TanStack Query, React Hook Form + Zod, Axios, React Router
- Cliente HTTP centralizado (`@/shared/services/api`) con interceptor de auth y refresh transparente de JWT (access token corto + refresh rotation), manejo de 401 → refresh → retry, y 403 → redirect
- Pantalla de Login: formulario email + contraseña + tenant_code, consume endpoint `POST /api/v1/auth/login`
- Pantalla de 2FA: formulario TOTP, consume endpoint `POST /api/v1/auth/2fa/challenge`
- Pantalla de Recuperación de contraseña: solicitud de recuperación (`POST /api/v1/auth/recovery`) y restablecimiento con token (`POST /api/v1/auth/recovery/reset`)
- Guard de rutas por permiso (`modulo:accion`): redirige a login si no hay sesión, muestra 403 si el usuario no tiene el permiso requerido
- Layout principal con sidebar/menú que se adapta a los permisos del usuario logueado (oculta secciones no autorizadas en el menú)
- Logout: revoca refresh token y limpia sesión local
- Tests: render de login, flujo de auth mockeado, guard redirige sin sesión, refresh transparente

## Capabilities

### New Capabilities
- `frontend-shell`: Scaffolding y configuración del proyecto frontend. Shared components, cliente HTTP centralizado con refresh transparente, layout shell con menú adaptativo. React Router con lazy loading de features.
- `frontend-auth`: Pantallas y lógica de autenticación: login, 2FA TOTP, recuperación de contraseña. Hooks y servicios de autenticación (login, logout, refresh, sesión), store de sesión, manejo de tokens.
- `frontend-route-guard`: Guard de rutas que verifica autenticación y permisos `modulo:accion` antes de permitir el acceso a una ruta. Redirección a login si no hay sesión, pantalla 403 si falta permiso.

### Modified Capabilities
<!-- No existing frontend specs exist. Backend specs remain unchanged. -->

## Impact

- Nuevo directorio `frontend/` con el proyecto completo
- No hay cambios en backend (las APIs ya existen y están estabilizadas)
- Las pantallas de auth consumen endpoints de `C-03` (`/api/v1/auth/*`)
- El guard de rutas usa la resolución de permisos del backend (`C-04`)
- Dependencias del proyecto: `react@18`, `typescript`, `vite`, `tailwindcss`, `@tanstack/react-query`, `react-hook-form`, `zod`, `axios`, `react-router-dom`
- Test setup: vitest + @testing-library/react + msw (mock service worker para mockear APIs)
