## ADDED Requirements

### Requirement: Registrar guardia
El sistema SHALL permitir a un TUTOR registrar una guardia con los datos: asignacion_id, materia_id, carrera_id, cohorte_id, día, horario, estado, comentarios. Cada guardia SHALL pertenecer al tenant del usuario autenticado.

#### Scenario: TUTOR registra guardia propia
- **WHEN** un TUTOR autenticado registra una guardia con asignacion_id=X, materia_id=Y, dia="Lunes", horario="14:00–14:45", estado="Pendiente"
- **THEN** el sistema crea la guardia con tenant_id del TUTOR
- **AND** retorna la guardia creada con su UUID

### Requirement: Consultar guardias
El sistema SHALL permitir consultar guardias del tenant con filtros opcionales por materia, carrera, cohorte, tutor, estado, y rango de fechas.

#### Scenario: COORDINADOR consulta guardias con filtros
- **WHEN** un COORDINADOR consulta guardias con materia_id=X
- **THEN** el sistema retorna las guardias del tenant que coinciden con el filtro
- **AND** cada guardia incluye datos del tutor asociado

### Requirement: Exportar guardias a CSV
El sistema SHALL proveer un endpoint que exporte las guardias filtradas a formato CSV, con header `Content-Disposition: attachment`.

#### Scenario: Exportar guardias filtradas
- **WHEN** un COORDINADOR solicita exportación CSV con materia_id=X
- **THEN** el sistema descarga un archivo CSV con las guardias filtradas
- **AND** el CSV incluye las columnas: tutor, materia, carrera, cohorte, día, horario, estado, comentarios, creada_at

### Requirement: Actualizar estado de guardia
El sistema SHALL permitir que un TUTOR actualice el estado de su propia guardia (Pendiente → Realizada | Cancelada).

#### Scenario: TUTOR marca guardia como Realizada
- **WHEN** un TUTOR actualiza estado de su guardia a "Realizada"
- **THEN** el sistema actualiza el estado
- **AND** registra la fecha de modificación
