## ADDED Requirements

### Requirement: Panel de auditoría y métricas
El frontend SHALL mostrar un dashboard con gráfico de acciones por día (volumen temporal), estado de comunicaciones agrupado por docente, interacciones por docente y materia, y log de últimas 200 acciones. SHALL incluir filtros por rango de fechas, materia, usuario y estado de actividad.

#### Scenario: Dashboard con gráficos
- **WHEN** el usuario con permiso `auditoria:ver` accede a `/admin/auditoria`
- **THEN** se muestra el panel con gráficos de acciones por día, estado de comunicaciones y tabla de últimas acciones

#### Scenario: Filtro de rango de fechas
- **WHEN** el usuario ajusta el filtro de fechas en el panel
- **THEN** los gráficos y tablas se actualizan para reflejar el rango seleccionado

#### Scenario: Filtro por materia
- **WHEN** el usuario selecciona una materia en el filtro
- **THEN** las métricas se actualizan mostrando solo datos de esa materia

### Requirement: Log completo de auditoría
El frontend SHALL mostrar el log cronológico de todas las acciones del sistema con campos: fecha/hora, usuario, materia, tipo de acción, cantidad de registros afectados, IP de origen y user agent. SHALL incluir paginación y filtros.

#### Scenario: Visualizar log completo
- **WHEN** el usuario accede a `/admin/auditoria/log`
- **THEN** se muestra una tabla paginada con el log cronológico de acciones

#### Scenario: Filtros combinados en log
- **WHEN** el usuario aplica filtros por usuario, materia y tipo de acción simultáneamente
- **THEN** la tabla se actualiza mostrando solo las entradas que cumplen todos los filtros
