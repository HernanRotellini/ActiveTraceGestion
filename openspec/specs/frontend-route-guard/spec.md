## ADDED Requirements

### Requirement: Authentication guard
The system SHALL redirect unauthenticated users to the login page when accessing protected routes.

#### Scenario: Unauthenticated user is redirected to login
- **WHEN** an unauthenticated user navigates to a protected route
- **THEN** the user is redirected to `/login` with the original URL as a `redirectTo` query parameter

#### Scenario: Authenticated user accesses protected route
- **WHEN** an authenticated user navigates to a protected route
- **THEN** the route is rendered normally

### Requirement: Permission guard
The system SHALL restrict access to routes based on the user's effective permissions, using `modulo:accion` format consistent with the backend RBAC.

#### Scenario: User with required permission accesses route
- **WHEN** an authenticated user with the required `modulo:accion` permission navigates to a permission-protected route
- **THEN** the route is rendered normally

#### Scenario: User without required permission sees 403 page
- **WHEN** an authenticated user without the required `modulo:accion` permission navigates to a permission-protected route
- **THEN** a 403 Forbidden page is rendered

#### Scenario: Multiple permission requirements can be specified
- **WHEN** a route requires multiple permissions (logical AND)
- **THEN** all must be present for access to be granted

### Requirement: Post-login redirect
The system SHALL redirect the user to the originally requested URL after successful login.

#### Scenario: Redirect after login uses redirectTo parameter
- **WHEN** an unauthenticated user is redirected to login and then authenticates successfully
- **THEN** the user is redirected to the URL specified in the `redirectTo` parameter

#### Scenario: Login without redirectTo goes to default route
- **WHEN** the user navigates to `/login` directly (no redirectTo) and authenticates successfully
- **THEN** the user is redirected to the default authenticated route (`/`)

### Requirement: 403 Forbidden page
The system SHALL render a dedicated 403 page when access is denied due to insufficient permissions.

#### Scenario: 403 page displays message
- **WHEN** a 403 page is rendered
- **THEN** it displays a clear message that the user does not have permission to access the requested resource

#### Scenario: 403 page includes navigation back
- **WHEN** a 403 page is rendered
- **THEN** it includes a link or button to navigate to a permitted section of the application
