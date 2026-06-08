## ADDED Requirements

### Requirement: Project scaffolding
The frontend SHALL be scaffolded as a React 18 + TypeScript project with Vite as bundler.

#### Scenario: Dev server starts successfully
- **WHEN** the project dev server is started with `npm run dev`
- **THEN** Vite starts HMR server and the app is accessible at the configured port

#### Scenario: TypeScript compilation passes
- **WHEN** `npx tsc --noEmit` is executed
- **THEN** no type errors are reported

### Requirement: Dependency integration
The project SHALL include and configure Tailwind CSS, TanStack Query, React Hook Form, Zod and Axios as direct dependencies.

#### Scenario: Tailwind utility classes render
- **WHEN** a component uses Tailwind utility classes
- **THEN** the CSS is correctly compiled and applied

#### Scenario: TanStack Query provider wraps the app
- **WHEN** the app renders
- **THEN** a QueryClientProvider wraps the component tree, configured with default staleTime and retry behavior

### Requirement: Shared HTTP client
The system SHALL provide a centralized Axios instance in `shared/services/api.ts` with JWT interceptors and transparent refresh.

#### Scenario: Request attaches access token
- **WHEN** a protected API request is made
- **THEN** the interceptor attaches `Authorization: Bearer <access_token>` from sessionStorage

#### Scenario: Expired access token is refreshed transparently
- **WHEN** a request returns 401 and a valid refresh token exists
- **THEN** the interceptor calls the refresh endpoint, stores the new tokens, and retries the original request

#### Scenario: Failed refresh clears session
- **WHEN** the refresh endpoint returns an error (token expired, revoked, or invalid)
- **THEN** the interceptor clears sessionStorage and redirects to `/login`

#### Scenario: 403 response is rejected without refresh
- **WHEN** a request returns 403 Forbidden
- **THEN** the interceptor rejects the response immediately without attempting refresh

### Requirement: Feature-based module structure
The frontend SHALL organize code in feature-based modules under `features/{name}/{components,hooks,services,types,pages}`.

#### Scenario: Auth feature follows the convention
- **WHEN** the auth feature is created
- **THEN** its code lives under `features/auth/` with subdirectories for components, hooks, services, types and pages

#### Scenario: New features can be added without modifying existing ones
- **WHEN** a future feature (e.g., comisiones) is added
- **THEN** it can be placed under its own `features/comisiones/` directory without touching auth or shell code

### Requirement: Shared UI components
The system SHALL provide a set of reusable UI components in `shared/components/`.

#### Scenario: Button component renders variants
- **WHEN** a Button component is used with `variant` prop (primary, secondary, danger, ghost)
- **THEN** the correct Tailwind styles for that variant are applied

#### Scenario: Input component displays validation error
- **WHEN** an Input component receives an `error` prop
- **THEN** the input border turns red and the error message is displayed below

### Requirement: React Router configuration
The system SHALL use React Router v6 with lazy-loaded feature pages.

#### Scenario: Lazy-loaded feature page renders
- **WHEN** a route is accessed for a lazy-loaded feature
- **THEN** React.Suspense shows a loading fallback and then renders the page component

#### Scenario: Unknown route shows 404 page
- **WHEN** a user navigates to a route that does not exist
- **THEN** a 404 page is rendered

### Requirement: Layout shell with adaptive menu
The system SHALL provide a MainLayout component with sidebar navigation that adapts to the user's permissions.

#### Scenario: Sidebar shows permitted menu items
- **WHEN** the user is authenticated and has specific permissions
- **THEN** the sidebar renders only menu items whose required permission is held by the user

#### Scenario: Sidebar hides unpermitted menu items
- **WHEN** the user lacks a permission required by a menu item
- **THEN** that menu item does not appear in the sidebar

#### Scenario: Logout button is visible in the layout
- **WHEN** the user is authenticated
- **THEN** a logout button or link is visible in the navbar
