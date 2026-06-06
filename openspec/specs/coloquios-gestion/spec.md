## ADDED Requirements

### Requirement: Crear convocatoria de coloquio

El sistema SHALL permitir a usuarios con permiso `coloquios:gestionar` crear una convocatoria de coloquio especificando materia, cohorte, tipo de evaluación, instancia (nombre) y los turnos disponibles con sus cupos máximos.

#### Scenario: Creación exitosa con turnos
- **WHEN** un COORDINADOR crea una convocatoria para materia PROG_I, cohorte MAR-2026, tipo Coloquio, instancia "Coloquio Final", con 2 turnos (2026-07-15 cupo 10, 2026-07-16 cupo 8)
- **THEN** el sistema crea la Evaluacion y 2 TurnoEvaluacion asociados, y retorna la convocatoria con sus turnos

#### Scenario: Creación sin turnos
- **WHEN** un COORDINADOR crea una convocatoria sin definir turnos
- **THEN** el sistema rechaza la operación con error de validación

#### Scenario: Permiso denegado
- **WHEN** un ALUMNO intenta crear una convocatoria
- **THEN** el sistema retorna 403 Forbidden

### Requirement: Importar alumnos a una convocatoria

El sistema SHALL permitir a usuarios con permiso `coloquios:gestionar` importar alumnos (por usuario_id) a una convocatoria existente, registrándolos en la tabla ConvocatoriaAlumno.

#### Scenario: Importación exitosa
- **WHEN** un COORDINADOR envía una lista de 5 usuario_id para importar a una convocatoria activa
- **THEN** el sistema crea 5 registros en ConvocatoriaAlumno y retorna la cantidad importada

#### Scenario: Importación duplicada
- **WHEN** un COORDINADOR importa un alumno que ya está en la convocatoria
- **THEN** el sistema ignora el duplicado y retorna la cantidad de nuevos importados

#### Scenario: Convocatoria no existe
- **WHEN** un COORDINADOR intenta importar alumnos a una convocatoria inexistente
- **THEN** el sistema retorna 404 Not Found

### Requirement: Listar convocatorias con métricas

El sistema SHALL listar las convocatorias del tenant con métricas operativas: total de alumnos convocados, reservas activas, cupos totales y cupos libres.

#### Scenario: Listado con métricas
- **WHEN** un COORDINADOR solicita el listado de convocatorias
- **THEN** el sistema retorna cada convocatoria con materia, instancia, cantidad de turnos, alumnos convocados, reservas activas y cupos libres agregados

#### Scenario: Filtro por materia
- **WHEN** un COORDINADOR solicita listado filtrado por materia_id
- **THEN** el sistema retorna solo las convocatorias de esa materia

### Requirement: Panel de métricas global

El sistema SHALL exponer un panel con métricas globales de coloquios: total de alumnos cargados en convocatorias, cantidad de convocatorias activas, reservas activas y notas registradas.

#### Scenario: Métricas globales
- **WHEN** un COORDINADOR solicita el panel de métricas
- **THEN** el sistema retorna: alumnos_convocados (entero), convocatorias_activas (entero), reservas_activas (entero), notas_registradas (entero)

### Requirement: Admin global — registrar resultados

El sistema SHALL permitir a ADMIN registrar resultados (nota_final) para alumnos en una convocatoria, creando o actualizando ResultadoEvaluacion.

#### Scenario: Registro de resultado exitoso
- **WHEN** un ADMIN registra nota "Aprobado" para un alumno en una convocatoria
- **THEN** el sistema crea ResultadoEvaluacion con la nota y el registrado_por

#### Scenario: Actualización de resultado
- **WHEN** un ADMIN registra una nueva nota para un alumno que ya tiene resultado
- **THEN** el sistema actualiza el registro existente

#### Scenario: Alumno no convocado
- **WHEN** un ADMIN intenta registrar resultado para un alumno no importado a la convocatoria
- **THEN** el sistema retorna 400 Bad Request

### Requirement: Admin global — agenda de reservas

El sistema SHALL permitir a ADMIN consultar la agenda consolidada de reservas activas de todas las convocatorias del tenant.

#### Scenario: Agenda consolidada
- **WHEN** un ADMIN solicita la agenda de reservas
- **THEN** el sistema retorna todas las reservas Activas con evaluacion_id, turno_id, fecha, alumno_id

### Requirement: Estado de convocatoria

El sistema SHALL soportar cambio de estado de una convocatoria entre Activa y Cerrada. Una convocatoria cerrada no admite nuevas reservas ni importación de alumnos.

#### Scenario: Cerrar convocatoria
- **WHEN** un COORDINADOR cierra una convocatoria activa
- **THEN** el sistema cambia el estado a Cerrada

#### Scenario: Reserva en convocatoria cerrada
- **WHEN** un ALUMNO intenta reservar en una convocatoria Cerrada
- **THEN** el sistema retorna 400 con mensaje "Convocatoria cerrada"
