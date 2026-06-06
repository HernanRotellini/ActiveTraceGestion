## ADDED Requirements

### Requirement: Crear slot de encuentro recurrente
El sistema SHALL permitir crear un SlotEncuentro con recurrencia semanal. Al crear el slot con `cant_semanas > 0`, el sistema SHALL generar automáticamente N instancias de InstanciaEncuentro con fechas = `fecha_inicio + (7 * i)` para i en `range(cant_semanas)`.
- El slot SHALL contener: asignacion_id, materia_id, titulo, hora, dia_semana, fecha_inicio, cant_semanas, meet_url, vig_desde.
- Cada instancia generada SHALL heredar: materia_id, titulo, hora, meet_url del slot.
- El estado inicial de cada instancia SHALL ser "Programado".

#### Scenario: Creación de slot recurrente exitosa
- **WHEN** un PROFESOR crea un slot con dia_semana="Lunes", hora="18:00", fecha_inicio="2026-06-01", cant_semanas=4
- **THEN** el sistema crea 1 SlotEncuentro y 4 InstanciaEncuentro con fechas 2026-06-01, 2026-06-08, 2026-06-15, 2026-06-22
- **AND** cada instancia tiene estado="Programado"

#### Scenario: Validación de modo recurrente vs único
- **WHEN** se crea un slot con cant_semanas=0 y sin fecha_unica
- **THEN** el sistema SHALL rechazar la operación con error de validación
- **WHEN** se crea un slot con cant_semanas=5 y fecha_unica no nula
- **THEN** el sistema SHALL rechazar la operación con error de validación

### Requirement: Crear instancia de encuentro único
El sistema SHALL permitir crear una InstanciaEncuentro sin slot asociado (slot_id = null), con fecha, hora, titulo y meet_url específicos.

#### Scenario: Creación de encuentro único exitosa
- **WHEN** un PROFESOR crea una instancia sin slot_id con fecha="2026-07-15", hora="10:00", titulo="Consulta pre-parcial"
- **THEN** el sistema crea 1 InstanciaEncuentro con slot_id=null y estado="Programado"

### Requirement: Editar instancia de encuentro
El sistema SHALL permitir modificar los campos estado, meet_url, video_url y comentario de una InstanciaEncuentro individual sin afectar al slot ni a otras instancias del mismo slot (RN-14).

#### Scenario: Actualizar estado a Realizado con grabación
- **WHEN** un PROFESOR edita una instancia con estado="Realizado", video_url="https://zoom.us/rec/abc123"
- **THEN** el sistema actualiza SOLO esa instancia
- **AND** el resto de instancias del mismo slot mantienen sus estados originales

#### Scenario: Actualizar meet_url de una instancia
- **WHEN** un PROFESOR actualiza meet_url de una instancia
- **THEN** el sistema actualiza el campo meet_url de esa instancia
- **AND** el slot permanece sin cambios

#### Scenario: Cancelar instancia individual
- **WHEN** un PROFESOR cambia estado de una instancia a "Cancelado"
- **THEN** la instancia queda con estado="Cancelado"
- **AND** las demás instancias del mismo slot no se ven afectadas

### Requirement: Generar bloque HTML para LMS
El sistema SHALL generar un fragmento HTML con la lista de encuentros programados de una materia, listo para copiar y pegar en el aula virtual del LMS. El HTML SHALL contener una tabla con columnas: fecha, hora, título, enlace, grabación, estado.

#### Scenario: Generar HTML de encuentros de una materia
- **WHEN** se solicita el HTML para materia_id=X
- **THEN** el sistema retorna un string HTML con una tabla de los encuentros activos de esa materia
- **AND** el HTML incluye enlaces clickeables para meet_url y video_url cuando existen

### Requirement: Vista admin de encuentros
El sistema SHALL proveer una vista transversal de todos los encuentros del tenant, accesible por COORDINADOR y ADMIN, con filtros por materia, rango de fechas, estado y docente.

#### Scenario: Consultar encuentros con filtros
- **WHEN** un COORDINADOR consulta encuentros con filtro materia_id=X y estado="Programado"
- **THEN** el sistema retorna solo las instancias de ese tenant que coinciden con los filtros
- **AND** los resultados incluyen datos del slot (si existe) y de la asignación asociada

### Requirement: No modificar slot después de creado
El sistema SHALL NO permitir modificar fecha_inicio ni cant_semanas de un SlotEncuentro existente. Para cambiar la recurrencia, se debe eliminar el slot (soft delete) y crear uno nuevo. Se SHALL permitir modificar titulo, meet_url y vigencia del slot.

#### Scenario: Rechazar modificación de fecha_inicio en slot
- **WHEN** se intenta modificar fecha_inicio de un slot existente
- **THEN** el sistema rechaza con error 400
