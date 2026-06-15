## ADDED Requirements

### Requirement: Listar carreras con envoltura paginada
El endpoint `GET /api/admin/carreras` DEBE devolver un objeto con `items` y `total` en lugar de un array plano.

#### Scenario: Respuesta con carreras existentes
- **WHEN** se llama `GET /api/admin/carreras`
- **THEN** la respuesta DEBE ser `{ "items": [...], "total": 2 }`

#### Scenario: Respuesta sin carreras
- **WHEN** no existen carreras en el tenant
- **THEN** la respuesta DEBE ser `{ "items": [], "total": 0 }`

### Requirement: Campos de CarreraResponse normalizados
CarreraResponse DEBE incluir los campos `activo: bool` (derivado de `estado`), `creada_en` (alias de `created_at`), y `descripcion` (string opcional).

#### Scenario: Carrera activa
- **WHEN** `estado = "activa"`
- **THEN** `activo` DEBE ser `true`

#### Scenario: Carrera inactiva
- **WHEN** `estado = "inactiva"`
- **THEN** `activo` DEBE ser `false`

#### Scenario: created_at mapeado a creada_en
- **WHEN** se devuelve una carrera
- **THEN** `creada_en` DEBE contener el mismo valor que `created_at`

#### Scenario: descripcion por defecto
- **WHEN** la carrera no tiene descripción
- **THEN** `descripcion` DEBE ser `""`

### Requirement: Listar cohortes con envoltura y filtro
`GET /api/admin/cohortes` DEBE devolver `{ items, total }` y aceptar `carrera_id` como query param opcional.

#### Scenario: Filtrar cohortes por carrera
- **WHEN** se llama `GET /api/admin/cohortes?carrera_id=<uuid>`
- **THEN** la respuesta DEBE contener solo cohortes de esa carrera

#### Scenario: Sin filtro devuelve todos
- **WHEN** se llama `GET /api/admin/cohortes` sin parámetros
- **THEN** la respuesta DEBE devolver todos los cohortes del tenant

### Requirement: Campos de CohorteResponse normalizados
CohorteResponse DEBE incluir `activo: bool` y `creada_en`.

#### Scenario: Cohorte activa
- **WHEN** `estado = "activa"`
- **THEN** `activo` DEBE ser `true`

### Requirement: Actualizar cohorte via PATCH
DEBE existir `PATCH /api/admin/cohortes/{cohorte_id}` que acepte `nombre`, `anio`, `vig_desde`, `vig_hasta`.

#### Scenario: Actualizar nombre de cohorte
- **WHEN** se envía `PATCH /api/admin/cohortes/{id}` con `{ "nombre": "2027" }`
- **THEN** el response DEBE devolver la cohorte actualizada con el nuevo nombre

### Requirement: Listar materias con envoltura y filtros
`GET /api/admin/materias` DEBE devolver `{ items, total }` y aceptar `carrera_id` y `cohorte_id` como query params opcionales.

#### Scenario: Filtrar materias por carrera y cohorte
- **WHEN** se llama `GET /api/admin/materias?carrera_id=<uuid>&cohorte_id=<uuid>`
- **THEN** la respuesta DEBE contener solo materias de esa carrera y cohorte

#### Scenario: Sin filtros devuelve todas
- **WHEN** se llama `GET /api/admin/materias` sin parámetros
- **THEN** la respuesta DEBE devolver todas las materias del tenant

### Requirement: Campos de MateriaResponse completos
MateriaResponse DEBE incluir `activo`, `creada_en`, `carrera_id`, `cohorte_id`, `carga_horaria`, `carrera_nombre` y `cohorte_nombre`.

#### Scenario: Materia con relaciones
- **WHEN** se devuelve una materia con carrera y cohorte asignados
- **THEN** `carrera_id`, `cohorte_id`, `carrera_nombre` y `cohorte_nombre` DEBEN estar presentes

#### Scenario: carga_horaria por defecto
- **WHEN** la materia no tiene carga horaria definida
- **THEN** `carga_horaria` DEBE ser `0`
