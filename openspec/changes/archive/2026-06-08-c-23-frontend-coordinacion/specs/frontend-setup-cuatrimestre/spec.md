## ADDED Requirements

### Requirement: Configuración del período académico (FL-03)
El sistema SHALL proveer una página de setup donde el COORDINADOR/ADMIN configure el cuatrimestre activo: fechas clave, programas por materia, vigencia.

#### Scenario: Página de setup carga datos actuales
- **WHEN** un usuario con `programas:admin` navega a `/coordinacion/setup`
- **THEN** se renderiza el formulario con la configuración actual del cuatrimestre

### Requirement: Gestión de fechas académicas
El sistema SHALL permitir definir las fechas clave del período: inicio de clases, fin de clases, período de exámenes, fechas de coloquios, feriados.

#### Scenario: Definir fecha clave
- **WHEN** un usuario agrega una nueva fecha académica (tipo, fecha, descripción)
- **THEN** la fecha se persiste y aparece en el calendario del período

#### Scenario: Editar fecha existente
- **WHEN** un usuario modifica una fecha académica existente
- **THEN** los cambios se persisten

### Requirement: Programas por materia
El sistema SHALL permitir asociar programas de estudio a cada materia para el período activo.

#### Scenario: Asociar programa a materia
- **WHEN** un usuario selecciona una materia y carga o selecciona su programa
- **THEN** la asociación materia-programa queda registrada para el período

#### Scenario: Listado de programas del período
- **WHEN** el usuario navega a la sección de programas
- **THEN** se muestra un listado de materias con sus programas asociados

### Requirement: Activar/desactivar período
El sistema SHALL permitir activar un período académico configurado y desactivar el anterior.

#### Scenario: Activar nuevo período
- **WHEN** un usuario completa la configuración y activa el nuevo período
- **THEN** el período pasa a estado activo y el anterior se desactiva

#### Scenario: Validación antes de activar
- **WHEN** el usuario intenta activar sin haber completado fechas clave obligatorias
- **THEN** el sistema muestra errores de validación indicando qué falta completar
