## ADDED Requirements

### Requirement: Listado de avisos
El sistema SHALL proveer una página con tabla paginada de avisos del tenant, con columnas título, scope, fecha de publicación, estado de acknowledgment.

#### Scenario: Listado muestra avisos del tenant
- **WHEN** un usuario con `avisos:ver` navega a `/coordinacion/avisos`
- **THEN** se renderiza una tabla paginada con los avisos del tenant activo

#### Scenario: Filtros por estado y fecha
- **WHEN** el usuario aplica filtros por estado (publicado/borrador) o rango de fechas
- **THEN** la tabla se actualiza mostrando solo los avisos que coinciden

### Requirement: Crear aviso con scope de destino
El sistema SHALL permitir crear avisos seleccionando el alcance: roles específicos, comisiones, o usuarios individuales.

#### Scenario: Crear aviso con scope por rol
- **WHEN** un usuario con `avisos:crear` completa el formulario, selecciona "Por rol" y elige uno o más roles
- **THEN** el aviso se crea con el scope especificado y queda en estado borrador

#### Scenario: Crear aviso con scope por comisión
- **WHEN** un usuario selecciona "Por comisión" y elige una o más comisiones
- **THEN** el aviso se crea con scope de comisión

#### Scenario: Crear aviso con scope individual
- **WHEN** un usuario selecciona "Por usuario" y elige destinatarios individuales
- **THEN** el aviso se crea con destinatarios específicos

### Requirement: Publicar aviso
El sistema SHALL permitir cambiar el estado de un aviso de borrador a publicado.

#### Scenario: Publicar aviso exitosamente
- **WHEN** un usuario con `avisos:crear` hace clic en "Publicar" en un aviso en borrador
- **THEN** el aviso cambia a estado publicado y se registra la fecha de publicación

### Requirement: Tracking de acknowledgment
El sistema SHALL mostrar el estado de acknowledgment de cada aviso: quién lo vio, quién falta, resumen de estadísticas.

#### Scenario: Vista de acknowledgment de aviso
- **WHEN** un usuario con `avisos:ver` abre el detalle de un aviso publicado
- **THEN** se muestra una tabla con destinatarios, fecha de lectura (o pendiente), y barra de progreso general

#### Scenario: Filtros en tracking
- **WHEN** el usuario filtra por "No leído" en la tabla de acknowledgment
- **THEN** se muestran solo los destinatarios que aún no leyeron el aviso

### Requirement: Editar y eliminar aviso
El sistema SHALL permitir editar avisos en borrador y eliminar (soft delete) avisos publicados o no.

#### Scenario: Editar aviso en borrador
- **WHEN** un usuario edita un aviso en estado borrador y guarda
- **THEN** los cambios se persisten

#### Scenario: Eliminar aviso
- **WHEN** un usuario elimina un aviso
- **THEN** el aviso se marca como eliminado (soft delete) y desaparece del listado activo
