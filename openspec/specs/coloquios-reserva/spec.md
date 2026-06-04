## ADDED Requirements

### Requirement: Reservar turno con cupo

El sistema SHALL permitir a un ALUMNO (usuario autenticado con permiso `coloquios:reservar`) reservar un turno en una convocatoria, siempre que el turno tenga cupo_restante > 0 y el alumno esté en ConvocatoriaAlumno. La reserva decrementa cupo_restante atómicamente.

#### Scenario: Reserva exitosa
- **WHEN** un ALUMNO convocado reserva un turno con cupo_restante = 5
- **THEN** el sistema crea la ReservaEvaluacion con estado Activa, decrementa cupo_restante a 4, y retorna la reserva creada

#### Scenario: Sin cupo disponible
- **WHEN** un ALUMNO convocado reserva un turno con cupo_restante = 0
- **THEN** el sistema rechaza con error "Sin cupo disponible"

#### Scenario: Alumno no convocado
- **WHEN** un ALUMNO no incluido en ConvocatoriaAlumno intenta reservar
- **THEN** el sistema rechaza con error "Alumno no habilitado para esta convocatoria"

#### Scenario: Reserva duplicada
- **WHEN** un ALUMNO con una reserva Activa existente intenta reservar otro turno en la misma convocatoria
- **THEN** el sistema rechaza con error "Ya tiene una reserva activa en esta convocatoria"

#### Scenario: Convocatoria cerrada
- **WHEN** un ALUMNO intenta reservar en una convocatoria con estado Cerrada
- **THEN** el sistema rechaza con error "Convocatoria cerrada"

### Requirement: Cancelar reserva

El sistema SHALL permitir a un ALUMNO cancelar su propia reserva activa, restituyendo el cupo en el TurnoEvaluacion correspondiente.

#### Scenario: Cancelación exitosa
- **WHEN** un ALUMNO cancela su reserva Activa en un turno con cupo_restante = 3
- **THEN** el sistema cambia el estado de la reserva a Cancelada, incrementa cupo_restante a 4

#### Scenario: Reserva ya cancelada
- **WHEN** un ALUMNO intenta cancelar una reserva ya en estado Cancelada
- **THEN** el sistema retorna 404 Not Found o error "Reserva no encontrada o ya cancelada"

### Requirement: Consultar turnos disponibles

El sistema SHALL listar los turnos de una convocatoria con su disponibilidad (fecha, cupo_maximo, cupo_restante) para que el ALUMNO pueda elegir.

#### Scenario: Listar turnos con disponibilidad
- **WHEN** un ALUMNO consulta los turnos de una convocatoria
- **THEN** el sistema retorna los turnos con fecha, hora_inicio, hora_fin, cupo_maximo y cupo_restante
