## ADDED Requirements

### Requirement: CRUD de carreras
El frontend SHALL permitir ADMIN gestionar carreras con formulario ABM, tabla paginada con filtros por nombre y estado.

#### Scenario: Listar carreras
- **WHEN** el usuario con permiso `estructura:gestionar` accede a `/admin/estructura/carreras`
- **THEN** se muestra una tabla paginada con todas las carreras del tenant

#### Scenario: Crear carrera
- **WHEN** el usuario completa el formulario de nueva carrera y envía
- **THEN** se crea la carrera y la tabla se actualiza

#### Scenario: Editar carrera
- **WHEN** el usuario selecciona "Editar" en una carrera
- **THEN** se navega a un formulario precargado y al enviar se actualiza el registro

### Requirement: CRUD de cohortes
El frontend SHALL permitir ADMIN gestionar cohortes asociadas a una carrera, con formulario ABM y filtros.

#### Scenario: Listar cohortes por carrera
- **WHEN** el usuario selecciona una carrera en `/admin/estructura/cohortes`
- **THEN** se muestra la tabla de cohortes de esa carrera

#### Scenario: Crear cohorte
- **WHEN** el usuario completa el formulario de nueva cohorte y envía
- **THEN** se crea la cohorte asociada a la carrera seleccionada

### Requirement: CRUD de materias
El frontend SHALL permitir ADMIN gestionar materias asociadas a una carrera/cohorte, con formulario ABM y filtros.

#### Scenario: Listar materias
- **WHEN** el usuario accede a `/admin/estructura/materias`
- **THEN** se muestra una tabla paginada de materias con filtros por carrera y cohorte

#### Scenario: Editar materia
- **WHEN** el usuario selecciona "Editar" en una materia
- **THEN** se navega a un formulario precargado y al enviar se actualiza el registro
