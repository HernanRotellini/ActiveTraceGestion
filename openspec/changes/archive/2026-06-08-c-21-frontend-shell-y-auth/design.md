## Context

El backend de activia-trace está completo (20 changes implementados) con APIs REST en `/api/v1/auth/*` (login, 2FA, refresh, recovery, logout), RBAC (`require_permission`), y multi-tenancy row-level. No existe frontend alguno — este change funda el proyecto frontend completo. Es la base sobre la que se construirán C-22, C-23 y C-24.

Stack decidido en ARQUITECTURA.md §2: React 18 + TypeScript + Vite + Tailwind + TanStack Query + React Hook Form + Zod + Axios. Sin `any`, sin class components.

## Goals / Non-Goals

**Goals:**
- Scaffold completo del proyecto frontend con estructura feature-based
- Cliente HTTP centralizado con refresh transparente de JWT (access 15 min + refresh rotation)
- Pantallas de Login, 2FA TOTP y Recuperación de contraseña
- Guard de rutas que verifica autenticación y permiso `modulo:accion`
- Layout shell con sidebar/menú adaptado a permisos del usuario logueado
- Logout seguro (revoca refresh token + limpia sesión local)
- Tests unitarios y de integración con mocks de API

**Non-Goals:**
- Features de dominio académico (C-22, C-23, C-24)
- Administración de usuarios, roles o permisos desde frontend (se hace desde backend)
- Portal del alumno ni SSO con Moodle (Fase 2)
- Impersonación desde frontend (se implementa en C-22 o posterior)
- Componentes de UI complejos tipo tabla de datos, drag & drop, etc.

## Decisions

### 1. Estructura de directorios

Feature-based modules según ARQUITECTURA.md §4:

```
frontend/src/
├── features/
│   ├── auth/          # Login, 2FA, password recovery
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── types/
│   │   └── pages/
│   └── (future: comisiones, atrasados, etc.)
├── shared/
│   ├── services/api.ts       # Axios centralizado + interceptor JWT
│   ├── components/           # UI reutilizable (Button, Input, Card, etc.)
│   ├── hooks/                # Hooks compartidos (useSession, usePermissions)
│   └── types/                # Tipos compartidos (User, Session, ApiError)
├── guards/                   # Route guards
├── layouts/                  # Layout principal (shell, sidebar, navbar)
├── routes/                   # React Router configuration
├── App.tsx
└── main.tsx
```

**Rationale**: Feature-based modules permiten que cada feature sea autocontenida (componentes, hooks, servicios, tipos y páginas en un solo directorio). Esto facilita el trabajo paralelo de múltiples agentes en C-22/23/24. React Router lazy-loades las pages de cada feature.

### 2. Cliente HTTP centralizado (`shared/services/api.ts`)

Instancia de Axios con:
- `baseURL` desde env (`VITE_API_URL` que apunta a `backend:8000` en dev)
- Interceptor de request: adjunta `Authorization: Bearer <access_token>` de sessionStorage (NUNCA de un parámetro de request — ver regla dura #8)
- Interceptor de response:
  - 200/201/204 → pasa
  - **401**: intenta refresh (usa refresh token almacenado), si el refresh es exitoso → retry original con nuevo access token. Si el refresh falla (token expirado/inválido/rotado) → limpia sesión, redirige a `/login`.
  - **403**: redirige a `/403` (sin sesión no debería ocurrir porque el guard ya bloquea)
  - Otros errores → reject con `ApiError` tipado

**Alternativa considerada**: fetch nativo. Descartado porque no tiene interceptores ni manejo nativo de retry. Axios es el estándar del proyecto.

**Pattern**: Usar TanStack Query con queryFn que llama a api.get/post/put/delete. Cada feature define sus hooks en `features/{x}/services/`. El interceptor de refresh es transparente — las features nunca manejan tokens.

### 3. Sesión y estado de auth

- La sesión se guarda en `sessionStorage` (no localStorage — más seguro contra XSS en ventanas compartidas)
- `sessionStorage` contiene: `{ access_token, refresh_token, user: { id, email, nombre, roles, permisos[] } }`
- Un `SessionContext` (React context) expone `{ session, login, logout, isAuthenticated, hasPermission }`
- Al recargar la página: el context checkea si hay tokens en sessionStorage, y si el access token es válido (decodifica client-side para exp, sin verificar firma). Si expiró, el interceptor de Axios intentará refresh automático en la primera request.

**¿Por qué no guardar permisos en el frontend para evitar llamadas?** Los permisos pueden cambiar sin re-login (ver spec `authorization-guard`). Resolvemos permisos server-side en cada request protegida. La copia local en `session.user.permisos` se usa SOLO para UI (mostrar/ocultar elementos de menú). El guard de rutas verifica permisos localmente como UX rápida, pero endpoints protegidos en backend siempre re-verifican.

### 4. Guard de rutas (`guards/PermissionGuard.tsx`)

Componente wrapper que:
1. Verifica `isAuthenticated` del SessionContext → si no, redirige a `/login` con `redirectTo`
2. Si requiere permiso (`permiso?: string`), verifica `hasPermission(permiso)` → si no, renderiza `ForbiddenPage`
3. Si pasa ambas verificaciones, renderiza `<Outlet />`

**Decision**: No hay roles en el guard. Los roles no se verifican — solo los permisos `modulo:accion`. Esto es consistente con el backend donde `require_permission` es la unidad de autorización.

**Nested guards**: Las rutas de features futuras (C-22+) usan `PermissionGuard` con el permiso específico de la feature (ej. `calificaciones:importar`).

### 5. Layout shell (`layouts/MainLayout.tsx`)

Componente que renderiza:
- Sidebar izquierdo (collapsible en mobile) con items de navegación filtrados por `hasPermission`
- Navbar superior (breadcrumb + info de usuario + botón logout)
- `<Outlet />` para el contenido de la ruta activa

**Menú adaptativo**: La lista de navegación se construye a partir de un `menuItems[]` donde cada item tiene `permiso?: string`. Si `permiso` está definido y el usuario no lo tiene, el item no se renderiza.

### 6. Pantallas de auth

| Pantalla | Ruta | Endpoint | Schema (React Hook Form + Zod) |
|----------|------|----------|-------------------------------|
| Login | `/login` | `POST /api/v1/auth/login` | `{ tenant_code: string, email: string, password: string }` |
| 2FA Challenge | `/auth/2fa` | `POST /api/v1/auth/2fa/challenge` | `{ challenge_token: string, code: string }` |
| Solicitar recuperación | `/auth/recuperar` | `POST /api/v1/auth/recovery` | `{ email: string }` |
| Restablecer contraseña | `/auth/restablecer` | `POST /api/v1/auth/recovery/reset` | `{ token: string, password: string, password_confirm: string }` |

**Flujo de login con 2FA**:
1. Usuario completa login → backend responde 200 con tokens si no tiene 2FA, o 202 con `challenge_token` si tiene 2FA
2. Si challenge_token → redirige a `/auth/2fa`
3. Usuario ingresa código TOTP → `POST /api/v1/auth/2fa/challenge` con challenge_token + code
4. Backend responde con access/refresh tokens → sesión establecida

### 7. Tests

- **Framework**: vitest + @testing-library/react + msw
- **Auth flow mock**: msw intercepta llamadas a `/api/v1/auth/*` y responde según el escenario
- **Casos**:
  - Login renderiza formulario y botón submit
  - Login exitoso redirige al dashboard
  - Login con 2FA muestra desafío y redirige a 2FA
  - Guard redirige a `/login` sin sesión
  - Guard muestra 403 sin permiso
  - Refresh transparente: mock de access expirado + refresh exitoso + retry de request original
  - Logout: revoca refresh token y limpia sesión
  - Password recovery solicitud y restablecimiento exitosos

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| [R1] Tokens en sessionStorage se pierden al cerrar pestaña (menos conveniente para el usuario) | Trade-off aceptado: menor superficie de ataque vs localStorage. Si el UX es un problema, migrar a httpOnly cookie en deploy. |
| [R2] La copia local de permisos en sessionStorage puede estar desactualizada | El backend re-verifica permisos en cada request protegida. La copia local es solo para UI/UX de menú. Se refresca en cada login. |
| [R3] El interceptor de refresh causa requests bloqueantes | El refresh es una única llamada async que resuelve una cola de requests en espera (patrón refresh queue). Ninguna request se pierde. |
| [R4] Lazy loading de features puede causar flash de carga | Usar React.Suspense con fallback global skeleton. Cada feature puede tener su propio Suspense boundary. |
