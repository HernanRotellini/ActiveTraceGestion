## 1. Project scaffolding

- [x] 1.1 Scaffold React 18 + TypeScript + Vite project in `frontend/` with `npm create vite@latest`
- [x] 1.2 Install and configure dependencies: tailwindcss, @tanstack/react-query, react-hook-form, @hookform/resolvers, zod, axios, react-router-dom
- [x] 1.3 Configure Tailwind CSS with `tailwind.config.js` and `@tailwind` directives in CSS entry point
- [x] 1.4 Set up TypeScript strict mode in `tsconfig.json` (no `any`, strictNullChecks)
- [x] 1.5 Create `frontend/` directory structure: features/, shared/, guards/, layouts/, routes/
- [x] 1.6 Configure Vite proxy for API requests to backend in dev (`VITE_API_URL`)
- [x] 1.7 Set up TanStack Query provider (`QueryClientProvider`) in App.tsx with default staleTime (30s) and retry (1)
- [x] 1.8 Set up React Router with lazy-loaded route definitions in `routes/index.tsx`
- [x] 1.9 Add `App.tsx` with RouterProvider and QueryClientProvider wrapper
- [x] 1.10 Add `vite-env.d.ts` for Vite env types and path alias `@/` pointing to `src/`

## 2. Shared HTTP client and API layer

- [x] 2.1 Create `shared/types/api.ts` with `ApiError` type and generic response envelope
- [x] 2.2 Create `shared/services/api.ts` with Axios instance configured with baseURL, timeout, and request interceptor for `Authorization: Bearer` header
- [x] 2.3 Implement response interceptor with 401 → refresh → retry logic (refresh queue pattern for concurrent requests)
- [x] 2.4 Implement refresh token storage and rotation in response interceptor
- [x] 2.5 Handle 403 response rejection without refresh attempt
- [x] 2.6 Handle network errors and 5xx with generic error messages

## 3. Shared UI components

- [x] 3.1 Create `shared/components/Button.tsx` with variant prop (primary, secondary, danger, ghost) and loading state
- [x] 3.2 Create `shared/components/Input.tsx` with label, error, and forwarded ref for React Hook Form
- [x] 3.3 Create `shared/components/Card.tsx` for content containers
- [x] 3.4 Create `shared/components/Spinner.tsx` for loading states
- [x] 3.5 Create `shared/components/Alert.tsx` for success/error/info messages

## 4. Session management

- [x] 4.1 Define `shared/types/session.ts` with `SessionUser`, `Session`, `LoginPayload` types
- [x] 4.2 Create `shared/hooks/useSession.ts` with SessionContext providing `{ session, login, logout, isAuthenticated, hasPermission }`
- [x] 4.3 Implement session restoration from sessionStorage on app init
- [x] 4.4 Implement `hasPermission(permission: string)` as local check against stored permissions list
- [x] 4.5 Create `shared/services/session.ts` with sessionStorage read/write/clear helpers

## 5. Auth feature — services and hooks

- [x] 5.1 Create `features/auth/services/auth.ts` with login, logout, refresh, challenge2fa, requestRecovery, resetPassword API calls using `shared/services/api.ts`
- [x] 5.2 Create `features/auth/types.ts` with LoginRequest, LoginResponse, ChallengeRequest, ChallengeResponse, RecoveryRequest, ResetRequest types
- [x] 5.3 Create `features/auth/hooks/useLogin.ts` with TanStack Query mutation for login, handling 2FA challenge response (202) vs direct session (200)
- [x] 5.4 Create `features/auth/hooks/useLogout.ts` with TanStack Query mutation for logout
- [x] 5.5 Create `features/auth/hooks/useChallenge2fa.ts` with mutation for TOTP challenge
- [x] 5.6 Create `features/auth/hooks/useRecovery.ts` and `useResetPassword.ts` mutations

## 6. Auth feature — Login page

- [x] 6.1 Create `features/auth/pages/LoginPage.tsx` with React Hook Form + Zod schema for tenant_code, email, password
- [x] 6.2 Integrate `useLogin` hook with form submission
- [x] 6.3 Handle login success (200) → store session + redirect to `redirectTo` or `/`
- [x] 6.4 Handle 2FA challenge (202) → store challenge_token, redirect to `/auth/2fa`
- [x] 6.5 Handle error states: invalid credentials (401), rate limit (429), network error
- [x] 6.6 Add link to password recovery page

## 7. Auth feature — 2FA Challenge page

- [x] 7.1 Create `features/auth/pages/Challenge2faPage.tsx` with TOTP code input form
- [x] 7.2 Integrate `useChallenge2fa` hook
- [x] 7.3 Handle success → store session + redirect
- [x] 7.4 Handle error: invalid/expired code
- [x] 7.5 Guard direct navigation: redirect to login if no challenge_token in context

## 8. Auth feature — Password recovery pages

- [x] 8.1 Create `features/auth/pages/RecoveryPage.tsx` with email form
- [x] 8.2 Integrate `useRecovery` hook, show success message (no account enumeration)
- [x] 8.3 Create `features/auth/pages/ResetPasswordPage.tsx` with new password and confirm password fields
- [x] 8.4 Integrate `useResetPassword` hook
- [x] 8.5 Handle success → redirect to `/login` with success flash
- [x] 8.6 Handle expired/used token error → redirect to recovery page

## 9. Route guard

- [x] 9.1 Create `guards/AuthGuard.tsx` that checks `isAuthenticated`, redirects to `/login?redirectTo=<current>` if false
- [x] 9.2 Create `guards/PermissionGuard.tsx` that checks `hasPermission(required)`, renders ForbiddenPage if false
- [x] 9.3 Create `pages/ForbiddenPage.tsx` with 403 message and navigation back link
- [x] 9.4 Create `pages/NotFoundPage.tsx` with 404 message
- [x] 9.5 Wire guards into route definitions in `routes/index.tsx`

## 10. Layout shell with adaptive menu

- [x] 10.1 Create `layouts/MainLayout.tsx` with sidebar + navbar + `<Outlet />` structure
- [x] 10.2 Define menu items array with label, route, icon, and optional required permission
- [x] 10.3 Implement sidebar menu filtering: render only items where user has the required permission
- [x] 10.4 Add user info display in navbar (name, email, role badge)
- [x] 10.5 Add responsive sidebar (collapsible on mobile, persistent on desktop)
- [x] 10.6 Implement logout button in navbar layout

## 11. Route definitions

- [x] 11.1 Define public routes: `/login`, `/auth/2fa`, `/auth/recuperar`, `/auth/restablecer`, `/403`, `/404`
- [x] 11.2 Define protected shell route with AuthGuard wrapping MainLayout and `<Outlet />`
- [x] 11.3 Define default authenticated route (`/`) with redirect to first permitted menu item or welcome page
- [x] 11.4 Ensure lazy loading (React.lazy + Suspense) for all page components

## 12. Tests

- [x] 12.1 Set up vitest, @testing-library/react, @testing-library/jest-dom, msw, happy-dom
- [x] 12.2 Configure `vitest.config.ts` with jsdom/happy-dom environment and path aliases
- [x] 12.3 Write test: LoginPage renders form elements
- [x] 12.4 Write test: successful login (mock 200) redirects to dashboard
- [x] 12.5 Write test: login with 2FA (mock 202) redirects to challenge page
- [x] 12.6 Write test: login with invalid credentials shows error message
- [x] 12.7 Write test: AuthGuard redirects unauthenticated user to `/login`
- [x] 12.8 Write test: AuthGuard allows authenticated user through
- [x] 12.9 Write test: PermissionGuard shows 403 for missing permission
- [x] 12.10 Write test: PermissionGuard allows access with correct permission
- [x] 12.11 Write test: transparent refresh — mock expired token → refresh success → original request retried
- [x] 12.12 Write test: logout clears session and redirects to login
- [x] 12.13 Write test: password recovery request shows success message
- [x] 12.14 Write test: password reset with valid token redirects to login
- [x] 12.15 Write test: 2FA form validates TOTP input (6 digits)
