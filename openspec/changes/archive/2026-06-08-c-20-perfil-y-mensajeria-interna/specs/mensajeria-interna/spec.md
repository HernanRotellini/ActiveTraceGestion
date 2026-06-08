# mensajeria-interna Specification

## Purpose
Provide an internal messaging system between registered users of the platform, organized in conversation threads (hilos), parallel to the external email communication system.

## ADDED Requirements

### Requirement: List conversation threads
The system SHALL list active conversation threads for the authenticated user, ordered by most recent activity.

#### Scenario: List my threads
- **WHEN** an authenticated user sends a GET to `/api/v1/inbox`
- **THEN** the system returns 200 with a list of threads where the user is a participant, ordered by `ultimo_mensaje_at` descending

#### Scenario: Empty inbox returns empty list
- **WHEN** an authenticated user with no threads sends a GET to `/api/v1/inbox`
- **THEN** the system returns 200 with an empty list

#### Scenario: Thread includes participant info and last message preview
- **WHEN** an authenticated user views their thread list
- **THEN** each thread includes asunto, participantes, ultimo_mensaje_at, and a preview of the last message

### Requirement: View conversation thread
The system SHALL display a full conversation thread with all its messages, paginated.

#### Scenario: View thread messages
- **WHEN** an authenticated user sends a GET to `/api/v1/inbox/{hilo_id}`
- **THEN** the system returns 200 with thread metadata and all messages, ordered by created_at ascending

#### Scenario: Non-participant gets 404
- **WHEN** a user who is NOT a participant in a thread sends a GET to `/api/v1/inbox/{hilo_id}`
- **THEN** the system returns 404 Not Found

### Requirement: Reply to a thread
The system SHALL allow participants to reply within a thread.

#### Scenario: Reply to thread
- **WHEN** an authenticated participant sends a POST to `/api/v1/inbox/{hilo_id}/responder` with `{ "cuerpo": "Gracias por la información" }`
- **THEN** the system returns 201 with the new message, and the thread's `ultimo_mensaje_at` is updated

#### Scenario: Non-participant cannot reply
- **WHEN** a user who is NOT a participant sends a POST to `/api/v1/inbox/{hilo_id}/responder`
- **THEN** the system returns 404 Not Found

### Requirement: Start a new conversation thread
The system SHALL allow any authenticated user to start a new conversation thread with one or more other users.

#### Scenario: Start new thread
- **WHEN** an authenticated user sends a POST to `/api/v1/inbox` with `{ "asunto": "Consulta sobre materia", "destinatarios": ["<uuid>"], "cuerpo": "Hola, necesito información" }`
- **THEN** the system returns 201 with the new thread and first message
- **AND** the remitente is automatically added as a participant

#### Scenario: Thread with non-existent user returns 404
- **WHEN** an authenticated user sends a POST to `/api/v1/inbox` with a destinatario UUID that does not exist
- **THEN** the system returns 404 Not Found

### Requirement: Tenant isolation
Threads and messages SHALL be isolated by tenant.

#### Scenario: Tenant isolation
- **WHEN** a user from tenant A starts a thread with a user from tenant B
- **THEN** the system returns 404 for the non-existent user (users from other tenants are invisible)

#### Scenario: Inbox only shows own tenant threads
- **WHEN** a user lists their inbox
- **THEN** only threads where all participants belong to the same tenant are visible
