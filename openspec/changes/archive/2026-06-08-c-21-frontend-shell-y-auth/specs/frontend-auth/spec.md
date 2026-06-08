## ADDED Requirements

### Requirement: Login page
The system SHALL provide a login page at `/login` with a form collecting tenant code, email and password.

#### Scenario: Login form renders correctly
- **WHEN** the user navigates to `/login`
- **THEN** a form with fields tenant_code, email, password and a submit button is displayed

#### Scenario: Successful login without 2FA redirects to dashboard
- **WHEN** the user submits valid credentials and 2FA is not enabled
- **THEN** the session is stored and the user is redirected to the default authenticated route

#### Scenario: Successful login with 2FA redirects to challenge
- **WHEN** a user with 2FA enabled submits valid credentials
- **THEN** the API returns a challenge_token and the user is redirected to `/auth/2fa`

#### Scenario: Invalid credentials show error
- **WHEN** the user submits invalid credentials
- **THEN** an inline error message is displayed and the user remains on `/login`

#### Scenario: Form validation prevents submission with empty fields
- **WHEN** the user attempts to submit the form with empty required fields
- **THEN** Zod schema validation blocks submission and shows validation errors

#### Scenario: Login respects rate limiting
- **WHEN** the API returns 429 Too Many Requests
- **THEN** a rate limit error message is displayed with retry guidance

### Requirement: 2FA challenge page
The system SHALL provide a 2FA challenge page at `/auth/2fa` for TOTP code entry.

#### Scenario: 2FA form renders with TOTP input
- **WHEN** the user is redirected with a challenge_token
- **THEN** a form with a 6-digit TOTP code input and submit button is displayed

#### Scenario: Valid TOTP code establishes session
- **WHEN** the user submits a valid TOTP code with the challenge_token
- **THEN** the session is stored and the user is redirected to the default authenticated route

#### Scenario: Invalid TOTP code shows error
- **WHEN** the user submits an invalid or expired TOTP code
- **THEN** an error message is displayed and the user remains on the 2FA page

#### Scenario: Direct navigation to 2FA without challenge redirects to login
- **WHEN** an unauthenticated user navigates directly to `/auth/2fa`
- **THEN** the user is redirected to `/login`

### Requirement: Password recovery flow
The system SHALL provide a password recovery flow with request and reset pages.

#### Scenario: Recovery request form renders
- **WHEN** the user navigates to `/auth/recuperar`
- **THEN** a form with an email input and submit button is displayed

#### Scenario: Recovery request submission shows success message
- **WHEN** the user submits a valid email
- **THEN** a success message is displayed regardless of whether the email exists (no account enumeration)

#### Scenario: Password reset form renders with token
- **WHEN** the user navigates to `/auth/restablecer?token=<recovery_token>`
- **THEN** a form with new password, confirm password and submit button is displayed

#### Scenario: Valid token resets password
- **WHEN** the user submits a new password with a valid unexpired recovery token
- **THEN** the password is updated and the user is redirected to `/login` with a success message

#### Scenario: Expired or used token shows error
- **WHEN** the user submits a reset with an expired or already-used token
- **THEN** an error message is displayed and the user is redirected to `/auth/recuperar`

#### Scenario: Password confirmation mismatch is prevented
- **WHEN** the user enters non-matching password and confirm password
- **THEN** Zod schema validation blocks submission and shows a mismatch error

### Requirement: Session management
The system SHALL manage the user session via React Context, storing tokens in sessionStorage.

#### Scenario: Session is restored from sessionStorage on page reload
- **WHEN** the user reloads the page with an active session
- **THEN** SessionContext restores the session from sessionStorage and marks the user as authenticated

#### Scenario: hasPermission checks local permission list
- **WHEN** `hasPermission("modulo:accion")` is called
- **THEN** it returns true if the user's stored permission list includes that permission, false otherwise

### Requirement: Logout
The system SHALL provide logout that revokes the refresh token and clears local session.

#### Scenario: Logout calls API and clears session
- **WHEN** the user clicks logout
- **THEN** `POST /api/v1/auth/logout` is called with the refresh token, sessionStorage is cleared, and the user is redirected to `/login`

#### Scenario: Logout handles API failure gracefully
- **WHEN** the logout API call fails (network error or token already revoked)
- **THEN** the local session is still cleared and the user is redirected to `/login`
