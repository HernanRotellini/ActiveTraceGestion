## ADDED Requirements

### Requirement: Listado de encuentros
El sistema SHALL proveer una página con tabla paginada de encuentros del tenant, con columnas materia, comisión, fecha, hora, aula, docente.

#### Scenario: Listado muestra encuentros
- **WHEN** un usuario con `encuentros:ver` navega a `/coordinacion/encuentros`
- **THEN** se renderiza una tabla paginada con los encuentros programados

#### Scenario: Filtros por fecha y materia
- **WHEN** el usuario aplica filtros por rango de fechas o materia
- **THEN** la tabla se actualiza mostrando solo los encuentros que coinciden

### Requirement: Admin de slots horarios
El sistema SHALL permitir definir y gestionar slots horarios para encuentros (día, hora inicio, hora fin, aula).

#### Scenario: Crear slot horario
- **WHEN** un usuario con `encuentros:admin` crea un nuevo slot horario
- **THEN** el slot queda disponible para asignación a encuentros

#### Scenario: Editar slot existente
- **WHEN** un usuario modifica los datos de un slot
- **THEN** los cambios se persisten

### Requirement: Admin de instancias de dictado
El sistema SHALL permitir gestionar instancias de dictado (fecha, slot, aula, docente asignado) para una comisión.

#### Scenario: Crear instancia de encuentro
- **WHEN** un usuario con `encuentros:admin` crea una nueva instancia de encuentro
- **THEN** la instancia queda registrada con su fecha, slot, aula y docente

#### Scenario: Editar instancia existente
- **WHEN** un usuario modifica fecha, aula o docente de una instancia
- **THEN** los cambios se reflejan en el calendario de encuentros

### Requirement: Registro de guardias
El sistema SHALL permitir registrar y gestionar guardias docentes para encuentros.

#### Scenario: Registrar guardia
- **WHEN** un usuario con `encuentros:admin` asigna un docente como guardia a un encuentro
- **THEN** la guardia queda registrada con fecha y docente asignado

#### Scenario: Listado de guardias
- **WHEN** un usuario navega a la sección de guardias
- **THEN** se muestra un listado con las guardias programadas y su estado
