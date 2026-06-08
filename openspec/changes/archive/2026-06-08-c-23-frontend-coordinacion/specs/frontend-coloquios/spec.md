## ADDED Requirements

### Requirement: Listado de coloquios
El sistema SHALL proveer una página con tabla paginada de evaluaciones de coloquio, con columnas materia, comisión, fecha, estado, cantidad de inscriptos.

#### Scenario: Listado muestra coloquios del tenant
- **WHEN** un usuario con `coloquios:ver` navega a `/coordinacion/coloquios`
- **THEN** se renderiza una tabla paginada con las evaluaciones de coloquio

#### Scenario: Filtros por materia y estado
- **WHEN** el usuario aplica filtros por materia o estado (abierto/cerrado/en_curso)
- **THEN** la tabla se actualiza

### Requirement: Admin de evaluaciones de coloquio
El sistema SHALL permitir crear y gestionar instancias de evaluación de coloquio (fecha, cupo, comisión, tribunal).

#### Scenario: Crear evaluación de coloquio
- **WHEN** un usuario con `coloquios:admin` crea una nueva evaluación
- **THEN** la evaluación se registra con fecha, cupo, comisión y tribunal asignado

#### Scenario: Editar evaluación existente
- **WHEN** un usuario modifica fecha, cupo o tribunal de una evaluación
- **THEN** los cambios se persisten

### Requirement: Gestión de reservas de coloquio
El sistema SHALL mostrar las reservas de alumnos para cada instancia de coloquio y permitir gestionarlas.

#### Scenario: Ver reservas de coloquio
- **WHEN** un usuario abre el detalle de una evaluación de coloquio
- **THEN** se muestra la lista de alumnos inscriptos con su estado (confirmado/en_espera/cancelado)

#### Scenario: Confirmar o cancelar reserva
- **WHEN** un usuario cambia el estado de una reserva
- **THEN** el cambio se persiste y se actualiza el cupo disponible

### Requirement: Registro de resultados
El sistema SHALL permitir registrar los resultados de cada coloquio (aprobado/desaprobado/ausente) por alumno.

#### Scenario: Cargar resultado individual
- **WHEN** un usuario selecciona un alumno y registra su resultado
- **THEN** el resultado queda registrado con la nota y el estado

#### Scenario: Carga masiva de resultados
- **WHEN** un usuario carga resultados para múltiples alumnos a la vez
- **THEN** todos los resultados se registran en una operación
