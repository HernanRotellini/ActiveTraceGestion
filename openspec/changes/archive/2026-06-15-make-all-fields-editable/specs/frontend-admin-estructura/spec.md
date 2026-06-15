## MODIFIED Requirements

### Requirement: CRUD de carreras
El frontend SHALL permitir ADMIN gestionar carreras con formulario ABM que incluya todos los campos mostrados.

#### Scenario: Editar carrera con todos los campos
- **WHEN** el usuario selecciona "Editar" en una carrera y modifica nombre, código y descripción
- **THEN** al enviar el formulario, el PATCH incluye `{ nombre, codigo, descripcion }` y la tabla se actualiza

### Requirement: CRUD de materias
El frontend SHALL permitir ADMIN gestionar materias con formulario ABM que incluya todos los campos mostrados.

#### Scenario: Editar materia con todos los campos
- **WHEN** el usuario selecciona "Editar" en una materia y modifica nombre, código y carga horaria
- **THEN** al enviar el formulario, el PATCH incluye `{ nombre, codigo, carga_horaria }` y la tabla se actualiza

### Requirement: CRUD de cohortes
El frontend SHALL permitir ADMIN gestionar cohortes correctamente sin enviar campos extra.

#### Scenario: Editar cohorte sin enviar carrera_id
- **WHEN** el usuario selecciona "Editar" en una cohorte y modifica nombre o año
- **THEN** al enviar el formulario, el PATCH incluye solo `{ nombre, anio }` (sin `carrera_id`)
