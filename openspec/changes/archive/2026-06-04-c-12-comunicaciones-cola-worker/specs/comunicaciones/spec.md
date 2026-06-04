## ADDED Requirements

### Requirement: Máquina de estados de Comunicacion (RN-15)

El modelo `Comunicacion` SHALL tener un ciclo de vida de estados con las siguientes transiciones válidas: Pendiente → Enviando, Pendiente → Cancelado, Enviando → Enviado, Enviando → Error. Cualquier otra transición SHALL ser rechazada por el sistema.

#### Scenario: Pendiente → Enviando es válida
- **WHEN** una comunicación en estado Pendiente se marca para envío
- **THEN** su estado cambia a Enviando

#### Scenario: Pendiente → Cancelado es válida
- **WHEN** una comunicación en estado Pendiente se cancela
- **THEN** su estado cambia a Cancelado

#### Scenario: Enviando → Enviado es válida
- **WHEN** el worker confirma la entrega de una comunicación en estado Enviando
- **THEN** su estado cambia a Enviado y se registra `enviado_at`

#### Scenario: Enviando → Error es válida
- **WHEN** el worker reporta fallo en el despacho de una comunicación en estado Enviando
- **THEN** su estado cambia a Error

#### Scenario: Enviado → Pendiente es inválida
- **WHEN** se intenta retroceder una comunicación de Enviado a Pendiente
- **THEN** el sistema rechaza la transición con error

#### Scenario: Cancelado → Pendiente es inválida
- **WHEN** se intenta reactivar una comunicación Cancelado
- **THEN** el sistema rechaza la transición con error

### Requirement: Destinatario cifrado AES-256 en reposo

El campo `destinatario` de `Comunicacion` SHALL almacenarse cifrado con AES-256 utilizando el helper centralizado de cifrado en reposo definido en `data-encryption-at-rest`. El descifrado SHALL ocurrir solo cuando se necesita exponer el destinatario en la UI de detalle o en el worker de despacho.

#### Scenario: Destinatario se almacena cifrado
- **WHEN** se crea una Comunicacion con `destinatario="alumno@example.com"`
- **THEN** el valor en la base de datos es ciphertext, no el email plano

#### Scenario: Destinatario se descifra correctamente
- **WHEN** se recupera una Comunicacion para mostrarla en detalle
- **THEN** el sistema descifra `destinatario` y retorna el email original

#### Scenario: Cifrado no expone el valor en logs
- **WHEN** ocurre un error al cifrar/descifrar `destinatario`
- **THEN** el mensaje de error no incluye el email en texto plano

### Requirement: Preview de comunicación con sustitución de variables (RN-16)

El endpoint `POST /api/comunicaciones/preview` SHALL recibir un template de asunto y cuerpo con variables de sustitución y un conjunto de datos de ejemplo, y SHALL retornar el asunto y cuerpo renderizados con las variables reemplazadas. Las variables SHALL seguir el formato `{{variable}}`.

#### Scenario: Preview con variables simples
- **WHEN** se envía asunto="Recordatorio {{nombre}}" y cuerpo="Hola {{nombre}}, tu materia es {{materia}}" con datos `{"nombre": "Juan", "materia": "Programación I"}`
- **THEN** el sistema retorna asunto="Recordatorio Juan" y cuerpo="Hola Juan, tu materia es Programación I"

#### Scenario: Preview sin variables
- **WHEN** se envía asunto="Aviso importante" y cuerpo="Sin variables en el texto"
- **THEN** el sistema retorna el mismo asunto y cuerpo sin modificar

#### Scenario: Preview con variable no provista
- **WHEN** se envía asunto="Hola {{nombre}}" sin proporcionar `nombre` en los datos
- **THEN** el sistema retorna el texto con `{{nombre}}` sin reemplazar (no falla)

### Requirement: Envío masivo con cola (F3.2)

El endpoint `POST /api/comunicaciones/enviar` SHALL recibir `materia_id`, `asunto`, `cuerpo` (con variables `{{nombre}}`, `{{materia}}`, `{{comision}}`) y SHALL encolar un `Comunicacion` por cada alumno atrasado de esa materia. Cada comunicación SHALL:
- Tener estado Pendiente
- Compartir el mismo `lote_id` (UUID generado en el momento del envío)
- Tener `destinatario` cifrado con el email del alumno (desde `EntradaPadron`)
- Tener las variables del cuerpo y asunto pre-sustituidas por alumno

#### Scenario: Envío masivo a materia con 3 atrasados
- **WHEN** se invoca `POST /api/comunicaciones/enviar` con `materia_id=X`
- **THEN** se crean 3 Comunicaciones (una por atrasado), todas con el mismo `lote_id` y estado Pendiente

#### Scenario: Envío masivo a materia sin atrasados
- **WHEN** se invoca `POST /api/comunicaciones/enviar` con `materia_id=X` y no hay atrasados
- **THEN** el sistema retorna 200 con `mensajes_creados=0` y no crea comunicaciones

#### Scenario: Envío masivo con aprobación obligatoria pendiente
- **WHEN** el tenant tiene `aprobacion_comunicaciones_obligatoria=true` y se encola un envío
- **THEN** las comunicaciones se crean en estado Pendiente y el worker NO las procesa hasta que se aprueben

### Requirement: Aprobación humana de comunicaciones (F3.3, RN-17)

El sistema SHALL soportar aprobación y cancelación de lotes y comunicaciones individuales. La aprobación de un lote SHALL transicionar todas las comunicaciones Pendiente → Enviando en ese lote. La cancelación SHALL transicionar Pendiente → Cancelado.

#### Scenario: Aprobar lote completo
- **WHEN** se invoca `POST /api/comunicaciones/lotes/{lote_id}/aprobar`
- **THEN** todas las comunicaciones Pendiente en ese lote pasan a Enviando

#### Scenario: Cancelar lote completo
- **WHEN** se invoca `POST /api/comunicaciones/lotes/{lote_id}/cancelar`
- **THEN** todas las comunicaciones Pendiente en ese lote pasan a Cancelado

#### Scenario: Aprobar comunicación individual
- **WHEN** se invoca `POST /api/comunicaciones/lotes/{lote_id}/aprobar` no aplica a individual, pero existe `POST /api/comunicaciones/{id}/cancelar` para individual
- **THEN** la comunicación individual Pendiente especificada pasa a Cancelado

#### Scenario: Cancelar comunicación individual
- **WHEN** se invoca `POST /api/comunicaciones/{id}/cancelar` con una comunicación Pendiente
- **THEN** esa comunicación pasa a Cancelado

#### Scenario: Cancelar comunicación ya enviada falla
- **WHEN** se intenta cancelar una comunicación en estado Enviado
- **THEN** el sistema rechaza con error por transición inválida

### Requirement: Listado y detalle de lotes

El sistema SHALL exponer endpoints para listar lotes con estados agregados y ver detalle de comunicaciones dentro de un lote.

#### Scenario: Listar lotes retorna resumen
- **WHEN** se invoca `GET /api/comunicaciones/lotes`
- **THEN** retorna lista de lotes con `lote_id`, `materia_id`, `total`, `pendientes`, `enviados`, `errores`, `cancelados`, `creado_at`

#### Scenario: Detalle de lote retorna comunicaciones
- **WHEN** se invoca `GET /api/comunicaciones/lotes/{lote_id}`
- **THEN** retorna el listado de comunicaciones en ese lote con su estado individual

### Requirement: Worker asíncrono de despacho

El sistema SHALL tener un worker asíncrono que consuma comunicaciones Pendiente (que no requieran aprobación, o que ya estén aprobadas) y las procese: Pendiente → Enviando → Enviado (o Error). Por ahora el envío real es un stub que simula éxito.

#### Scenario: Worker procesa comunicación Pendiente
- **WHEN** el worker encuentra una comunicación en estado Pendiente que no requiere aprobación
- **THEN** la transiciona a Enviando, ejecuta el stub de envío, y la pasa a Enviado con `enviado_at` registrado

#### Scenario: Worker no procesa comunicación Pendiente con aprobación pendiente
- **WHEN** el worker encuentra una comunicación en estado Pendiente con `aprobacion_comunicaciones_obligatoria=true` y el lote no fue aprobado
- **THEN** el worker salta esa comunicación (no la procesa)

#### Scenario: Worker registra Error si stub falla
- **WHEN** el stub de envío simula un fallo
- **THEN** la comunicación pasa a estado Error

### Requirement: Tenant isolation en comunicaciones

Todas las operaciones sobre Comunicaciones SHALL estar aisladas por tenant. Un usuario del tenant A no puede ver ni operar sobre comunicaciones del tenant B.

#### Scenario: Listado de lotes aislado por tenant
- **WHEN** un usuario del tenant A lista lotes
- **THEN** solo ve lotes creados en el tenant A

#### Scenario: Aprobación de lote aislada por tenant
- **WHEN** un usuario del tenant A intenta aprobar un lote del tenant B
- **THEN** el sistema retorna 404 (no existe) por isolation

### Requirement: Autorización (comunicacion:enviar, comunicacion:aprobar)

Los endpoints de comunicaciones SHALL requerir los permisos correspondientes mediante el guard `require_permission(...)`.

#### Scenario: Usuario con comunicacion:enviar accede a endpoints de envío
- **WHEN** un usuario con permiso `comunicacion:enviar` invoca `POST /api/comunicaciones/preview`
- **THEN** el sistema retorna 200

#### Scenario: Usuario sin comunicacion:enviar recibe 403
- **WHEN** un usuario sin permiso `comunicacion:enviar` invoca `POST /api/comunicaciones/preview`
- **THEN** el sistema retorna 403 Forbidden

#### Scenario: Usuario con comunicacion:aprobar puede aprobar lotes
- **WHEN** un usuario con permiso `comunicacion:aprobar` invoca `POST /api/comunicaciones/lotes/{lote_id}/aprobar`
- **THEN** el sistema ejecuta la aprobación

#### Scenario: Usuario sin comunicacion:aprobar no puede aprobar
- **WHEN** un usuario sin permiso `comunicacion:aprobar` invoca `POST /api/comunicaciones/lotes/{lote_id}/aprobar`
- **THEN** el sistema retorna 403 Forbidden

### Requirement: Audit trail en comunicaciones

Las operaciones de envío, aprobación y cancelación de comunicaciones SHALL generar registros en el audit log con acciones `COMUNICACION_ENVIAR`, `COMUNICACION_APROBAR` y `COMUNICACION_CANCELAR` respectivamente.

#### Scenario: Envío masivo genera audit entry
- **WHEN** se ejecuta `POST /api/comunicaciones/enviar`
- **THEN** se crea un audit log con action `COMUNICACION_ENVIAR`, actor, materia_id y cantidad de mensajes

#### Scenario: Aprobación de lote genera audit entry
- **WHEN** se ejecuta `POST /api/comunicaciones/lotes/{lote_id}/aprobar`
- **THEN** se crea un audit log con action `COMUNICACION_APROBAR`, actor y lote_id

#### Scenario: Cancelación genera audit entry
- **WHEN** se cancela un lote o comunicación individual
- **THEN** se crea un audit log con action `COMUNICACION_CANCELAR`, actor y lote_id o comunicacion_id
