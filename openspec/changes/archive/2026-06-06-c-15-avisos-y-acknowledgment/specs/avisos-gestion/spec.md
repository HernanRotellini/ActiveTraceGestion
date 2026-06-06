# Spec: avisos-gestion

> Tablón de avisos institucionales con alcance configurable, vigencia programada, orden de prioridad y confirmación de lectura (acknowledgment).

---

## ADDED Requirements

### Requirement: Crear aviso

El sistema SHALL permitir a usuarios con permiso `avisos:publicar` crear un aviso con los siguientes campos:
- `titulo` (string, 200 caracteres máximo, requerido)
- `cuerpo` (texto enriquecido Markdown, requerido)
- `alcance` (enum: Global | PorMateria | PorCohorte | PorRol, requerido)
- `materia_id` (UUID, requerido si alcance=PorMateria, nullable otherwise)
- `cohorte_id` (UUID, requerido si alcance=PorCohorte, nullable otherwise)
- `rol_destino` (enum, requerido si alcance=PorRol, nullable otherwise)
- `severidad` (enum: Info | Advertencia | Crítico, default: Info)
- `inicio_en` (datetime, requerido)
- `fin_en` (datetime, nullable — sin límite si nulo)
- `orden` (integer, default: 0 — menor = mayor prioridad)
- `requiere_ack` (boolean, default: false)
- `activo` (boolean, default: true)

#### Scenario: Creación exitosa de aviso Global
- **WHEN** un COORDINADOR crea un aviso con alcance Global, titulo, cuerpo, severidad Info, inicio_en y fin_en definidos
- **THEN** el sistema retorna 201 con el aviso creado, y el aviso es visible para todos los usuarios del tenant

#### Scenario: Creación sin titulo rechazada
- **WHEN** un ADMIN intenta crear un aviso sin titulo
- **THEN** el sistema retorna 422 con error de validación

#### Scenario: Creación con alcance PorMateria sin materia_id rechazada
- **WHEN** un COORDINADOR crea un aviso con alcance PorMateria pero sin materia_id
- **THEN** el sistema retorna 422 indicando que materia_id es requerido para alcance PorMateria

#### Scenario: Creación con alcance PorCohorte sin cohorte_id rechazada
- **WHEN** un ADMIN crea un aviso con alcance PorCohorte pero sin cohorte_id
- **THEN** el sistema retorna 422 indicando que cohorte_id es requerido para alcance PorCohorte

#### Scenario: Creación con alcance PorRol sin rol_destino rechazada
- **WHEN** un COORDINADOR crea un aviso con alcance PorRol pero sin rol_destino
- **THEN** el sistema retorna 422 indicando que rol_destino es requerido para alcance PorRol

#### Scenario: Usuario sin permiso no puede crear aviso
- **WHEN** un PROFESOR intenta crear un aviso
- **THEN** el sistema retorna 403

---

### Requirement: Listar avisos visibles

El sistema SHALL retornar los avisos visibles para el usuario autenticado, aplicando los siguientes filtros automáticos:
1. `activo = true`
2. `inicio_en <= NOW()`
3. `fin_en IS NULL OR fin_en >= NOW()`
4. El alcance debe coincidir con el perfil del usuario:
   - `Global`: visible para todos
   - `PorRol`: el rol del usuario está en `rol_destino`
   - `PorMateria`: el usuario tiene asignaciones en `materia_id`
   - `PorCohorte`: el usuario tiene asignaciones en `cohorte_id`
5. Ordenados por `orden ASC`, luego `inicio_en DESC`

#### Scenario: Usuario ve avisos Globales
- **WHEN** un TUTOR autenticado consulta `GET /api/avisos`
- **THEN** la respuesta incluye todos los avisos con alcance Global activos y dentro de vigencia

#### Scenario: Usuario ve avisos PorRol
- **WHEN** un PROFESOR autenticado consulta `GET /api/avisos`
- **THEN** la respuesta incluye avisos con alcance PorRol donde rol_destino es PROFESOR

#### Scenario: Usuario NO ve avisos de otro rol
- **WHEN** un ALUMNO autenticado consulta `GET /api/avisos`
- **THEN** la respuesta NO incluye avisos con alcance PorRol donde rol_destino es COORDINADOR

#### Scenario: Usuario ve avisos PorMateria de sus materias
- **WHEN** un PROFESOR con asignaciones en materia X consulta `GET /api/avisos`
- **THEN** la respuesta incluye avisos con alcance PorMateria y materia_id = X

#### Scenario: Usuario NO ve avisos PorMateria de materias no asignadas
- **WHEN** un PROFESOR sin asignaciones en materia Y consulta `GET /api/avisos`
- **THEN** la respuesta NO incluye avisos con alcance PorMateria y materia_id = Y

#### Scenario: Aviso fuera de vigencia no se muestra
- **WHEN** un usuario consulta `GET /api/avisos` y existe un aviso cuyo fin_en es anterior a NOW()
- **THEN** ese aviso NO aparece en la respuesta

#### Scenario: Aviso inactivo no se muestra
- **WHEN** un usuario consulta `GET /api/avisos` y existe un aviso con activo=false
- **THEN** ese aviso NO aparece en la respuesta

#### Scenario: Aviso futuro no se muestra
- **WHEN** un usuario consulta `GET /api/avisos` y existe un aviso cuyo inicio_en es posterior a NOW()
- **THEN** ese aviso NO aparece en la respuesta

#### Scenario: Avisos ordenados por prioridad
- **WHEN** un usuario consulta `GET /api/avisos` y existen múltiples avisos visibles
- **THEN** la respuesta los retorna ordenados por `orden` ASC (menor primero), y en caso de empate por `inicio_en` DESC

---

### Requirement: Confirmar lectura de aviso (acknowledgment)

El sistema SHALL permitir a cualquier usuario autenticado confirmar la lectura de un aviso mediante `POST /api/avisos/{id}/ack`. La confirmación SHALL ser idempotente: si el usuario ya confirmó, el segundo POST es no-op y retorna 200.

#### Scenario: Confirmación exitosa
- **WHEN** un usuario autenticado envía `POST /api/avisos/{id}/ack` para un aviso visible
- **THEN** el sistema crea un registro en AcknowledgmentAviso y retorna 200

#### Scenario: Confirmación idempotente
- **WHEN** un usuario autenticado envía `POST /api/avisos/{id}/ack` dos veces para el mismo aviso
- **THEN** la segunda solicitud retorna 200 sin crear un duplicado

#### Scenario: Confirmación de aviso inexistente
- **WHEN** un usuario autenticado envía `POST /api/avisos/{id}/ack` para un aviso que no existe
- **THEN** el sistema retorna 404

#### Scenario: Confirmación sin autenticación
- **WHEN** un usuario no autenticado envía `POST /api/avisos/{id}/ack`
- **THEN** el sistema retorna 401

---

### Requirement: Listar avisos pendientes de acknowledgment

El sistema SHALL exponer un endpoint `GET /api/avisos/pendientes-ack` que retorna solo los avisos visibles que:
1. Tienen `requiere_ack = true`
2. El usuario actual NO ha confirmado aún (no existe registro en AcknowledgmentAviso)

#### Scenario: Usuario tiene avisos pendientes de ack
- **WHEN** un usuario autenticado consulta `GET /api/avisos/pendientes-ack` y existen avisos con requiere_ack=true que no ha confirmado
- **THEN** la respuesta incluye esos avisos

#### Scenario: Todos los avisos confirmados
- **WHEN** un usuario autenticado consulta `GET /api/avisos/pendientes-ack` y ya confirmó todos los avisos con requiere_ack=true
- **THEN** la respuesta es una lista vacía

---

### Requirement: Administrar avisos (CRUD admin)

El sistema SHALL exponer endpoints de administración bajo `/api/admin/avisos/*` para usuarios con permiso `avisos:publicar`:
- `GET /api/admin/avisos` — listar todos los avisos (incluyendo inactivos y fuera de vigencia), con filtros opcionales: alcance, severidad, activo, rango de fechas
- `GET /api/admin/avisos/{id}` — detalle completo de un aviso
- `PUT /api/admin/avisos/{id}` — modificar un aviso (mismos campos que creación)
- `DELETE /api/admin/avisos/{id}` — desactivar aviso (soft delete: activo=false). El borrado físico queda reservado para operaciones de admin de DB.

#### Scenario: Admin lista todos los avisos
- **WHEN** un ADMIN consulta `GET /api/admin/avisos`
- **THEN** la respuesta incluye todos los avisos del tenant, incluyendo inactivos y fuera de vigencia

#### Scenario: Admin filtra avisos por severidad
- **WHEN** un ADMIN consulta `GET /api/admin/avisos?severidad=Critico`
- **THEN** la respuesta incluye solo avisos con severidad Crítico

#### Scenario: Admin actualiza aviso
- **WHEN** un ADMIN envía `PUT /api/admin/avisos/{id}` con nuevos valores para titulo y cuerpo
- **THEN** el sistema retorna 200 con el aviso actualizado

#### Scenario: Admin desactiva aviso
- **WHEN** un COORDINADOR envía `DELETE /api/admin/avisos/{id}`
- **THEN** el sistema marca activo=false y retorna 200 (el registro no se elimina físicamente)

#### Scenario: Usuario sin permiso no puede administrar
- **WHEN** un TUTOR intenta acceder a `GET /api/admin/avisos`
- **THEN** el sistema retorna 403

---

### Requirement: Estadísticas de aviso

El sistema SHALL exponer `GET /api/admin/avisos/{id}/stats` con:
- `total_acks`: cantidad de registros en AcknowledgmentAviso para ese aviso
- `usuarios_sin_confirmar`: (si requiere_ack=true) lista de usuarios destinatarios que aún no confirmaron

#### Scenario: Estadísticas de aviso con requiere_ack=true
- **WHEN** un ADMIN consulta `GET /api/admin/avisos/{id}/stats` para un aviso con requiere_ack=true y 5 de 10 destinatarios confirmaron
- **THEN** la respuesta incluye total_acks=5 y una lista de 5 usuarios sin confirmar

#### Scenario: Estadísticas de aviso sin requiere_ack
- **WHEN** un ADMIN consulta `GET /api/admin/avisos/{id}/stats` para un aviso con requiere_ack=false
- **THEN** la respuesta incluye total_acks y usuarios_sin_confirmar como null o lista vacía

---

### Requirement: Aislamiento multi-tenant

El sistema SHALL garantizar que los avisos y acknowledgments de un tenant NO sean visibles para usuarios de otro tenant.

#### Scenario: Aislamiento de avisos entre tenants
- **WHEN** un usuario del tenant A consulta `GET /api/avisos`
- **THEN** la respuesta NO incluye avisos del tenant B

#### Scenario: Aislamiento de estadísticas entre tenants
- **WHEN** un ADMIN del tenant A consulta `GET /api/admin/avisos/{id}/stats`
- **THEN** la respuesta NO incluye acknowledgments de usuarios del tenant B

---

### Requirement: Auditoría de operaciones

El sistema SHALL registrar en AuditLog las siguientes operaciones sobre avisos:
- `AVISO_CREAR` — creación de aviso
- `AVISO_MODIFICAR` — modificación de aviso
- `AVISO_DESACTIVAR` — desactivación de aviso
- `AVISO_ACK` — confirmación de lectura

#### Scenario: Auditoría al crear aviso
- **WHEN** un COORDINADOR crea un aviso exitosamente
- **THEN** el sistema registra un AuditLog con accion=AVISO_CREAR, actor_id=COORDINADOR, detalle con id del aviso

#### Scenario: Auditoría al confirmar lectura
- **WHEN** un usuario confirma lectura de un aviso
- **THEN** el sistema registra un AuditLog con accion=AVISO_ACK, actor_id=usuario, detalle con aviso_id
