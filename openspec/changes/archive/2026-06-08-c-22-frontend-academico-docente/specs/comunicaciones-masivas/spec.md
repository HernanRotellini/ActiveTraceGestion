## ADDED Requirements

### Requirement: Preview de comunicación antes del envío
The system SHALL show a preview of the message (subject + body) before the user confirms sending.

#### Scenario: Generate preview for selected students
- **WHEN** the user selects one or more atrasados students and clicks "preview"
- **THEN** the system POSTs to `/api/v1/comunicaciones/preview` and displays the rendered subject and body as the students will receive it

#### Scenario: Preview renders correctly
- **WHEN** the preview is displayed
- **THEN** it shows the exact subject line and body, including any personalized fields (student name, subject, etc.)

### Requirement: Enviar comunicación a atrasados
The system SHALL send communication messages to selected atrasados students via the async queue.

#### Scenario: Confirm and send
- **WHEN** the user reviews the preview and clicks "send"
- **THEN** the system POSTs to `/api/v1/comunicaciones/enviar` and shows a success notification; each message enters the queue as "Pendiente"

#### Scenario: Send button disabled without selection
- **WHEN** no students are selected
- **THEN** the send button is disabled

#### Scenario: Send fails with server error
- **WHEN** the API returns an error
- **THEN** the system shows an error notification with the server message

### Requirement: Tracking de estado en tiempo real
The system SHALL display real-time status of sent communications with polling.

#### Scenario: Status timeline updates
- **WHEN** the user views the tracking panel for a sent communication
- **THEN** the system polls `GET /api/v1/comunicaciones/{id}` every 5 seconds and updates the status badge (Pendiente → Enviando → OK/Fallido/Cancelado)

#### Scenario: All messages delivered
- **WHEN** all messages reach terminal state (OK/Fallido/Cancelado)
- **THEN** the system stops polling and shows a summary: "X enviados, Y fallidos, Z cancelados"

#### Scenario: Communication not found
- **WHEN** the communication ID does not exist
- **THEN** the system shows a "Comunicación no encontrada" error state
