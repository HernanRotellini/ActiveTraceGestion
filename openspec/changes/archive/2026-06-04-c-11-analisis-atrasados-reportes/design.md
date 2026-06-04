## Context

C-10 entregó `Calificacion` (nota numérica/textual con `aprobado` derivado) y `UmbralMateria` (umbral por asignación docente). C-09 entregó `EntradaPadron` y `VersionPadron` (padrón versionado por materia×cohorte). C-06 entregó `Materia`, `Carrera`, `Cohorte`. C-07 entregó `Asignacion` (usuario ↔ rol ↔ contexto académico).

Sobre estos datos, C-11 debe resolver consultas agregadas sin nuevas tablas: detectar alumnos atrasados (RN-06), rankear aprobados (RN-09), calcular notas finales agrupadas, exportar TPs sin corregir (RN-07/08), y exponer monitores filtrados.

## Goals / Non-Goals

**Goals:**
- Proveer endpoints de consulta (GET) para atrasados, ranking, reportes rápidos, notas finales, monitores.
- Proveer endpoint de exportación (GET descarga archivo) para TPs sin corregir.
- Toda lógica de cálculo en Services; Repositories ejecutan queries SQLAlchemy; Routers solo orquestan.
- Guard `atrasados:ver` en todos los endpoints; scope `(propio)` para TUTOR/PROFESOR (solo sus asignaciones), scope global para COORDINADOR/ADMIN.
- Audit log para exportaciones (`ANALISIS_EXPORTAR`) y consultas de monitores (`ANALISIS_CONSULTAR`).
- Base de datos relacional — no se introducen motores de búsqueda, caché ni OLAP.

**Non-Goals:**
- No se crean nuevas tablas ni migraciones de schema.
- No hay cálculos asincrónicos ni caché precomputada (las consultas se resuelven en tiempo real).
- No hay integración con sistemas externos — solo datos del sistema.
- No hay endpoints de escritura salvo el registro de auditoría.

## Decisions

### D-01: Computar atrasados vía query SQL agregada, no en aplicación
**Context**: Determinar si un alumno está atrasado (RN-06) requiere cruzar el padrón activo contra las calificaciones existentes y los umbrales.
**Decision**: El Repository ejecuta una query SQLAlchemy que, para cada `EntradaPadron` del padrón activo de una materia, detecta:
- Actividades sin calificación (faltantes: cruce contra actividades reales en `Calificacion`).
- Actividades con nota < umbral configurado.
- Retorna lista de alumnos + detalle de actividades atrasadas.
**Rationale**: Traer todas las calificaciones a la aplicación para filtrar en Python no escala a decenas de alumnos × múltiples actividades. La agregación en SQL es la herramienta correcta.
**Alternativa considerada**: Computar en Python post-query. Se descarta por rendimiento: una materia puede tener 50+ alumnos × 10+ actividades = 500+ registros; la lógica de comparación es simple (umbral vs nota).

### D-02: Ranking como query ordenada con HAVING COUNT
**Context**: RN-09 exige excluir alumnos sin ninguna actividad aprobada.
**Decision**: Query que agrupa por `entrada_padron_id`, filtra con `HAVING COUNT(*) FILTER (WHERE aprobado = true) >= 1`, ordena descendente por count de aprobadas.
**Rationale**: Es una agregación directa en SQL con having filter. No hay joins complejos ni subconsultas anidadas.

### D-03: Notas finales agrupadas como promedio ponderado de actividades seleccionadas
**Context**: F2.5 pide agrupar actividades configuradas y calcular una nota final por alumno.
**Decision**: El endpoint acepta un listado de nombres de actividad a incluir. Calcula el promedio de `nota_numerica` para esas actividades por alumno. Si el alumno no tiene todas las actividades seleccionadas, se computa sobre las existentes. El campo `aprobado` de la nota final se deriva contra el umbral de la materia.
**Rationale**: No hay un modelo de "nota final" persistente — es un cálculo ad-hoc sobre las actividades que el docente seleccione. El promedio simple es la operación más predecible.

### D-04: Exportación de TPs sin corregir como archivo descargable
**Context**: F2.6 requiere exportar el listado de entregas detectadas como pendientes de corrección.
**Decision**: El service reusa la lógica de detección de TPs sin nota (reporte de finalización de C-10 + filtro RN-08) y genera un CSV con columnas: alumno, actividad, materia, comisión, fecha de entrega. El Router devuelve `StreamingResponse` con `Content-Disposition: attachment`.
**Rationale**: CSV es universal, no requiere librerías adicionales y es el formato esperado por los docentes para seguimiento fuera del sistema.

### D-05: Monitores como endpoints query con filtros opcionales
**Context**: F2.7–F2.9 definen tres monitores con distintos alcances y filtros.
**Decision**: Un solo endpoint `/api/analisis/monitor` con parámetros query opcionales:
- `rol_vista`: `tutor` (propio), `coordinador` (tenant), `admin` (tenant + rango fechas).
- `materia_id`, `regional`, `comision`, `busqueda` (nombre/apellido/alumno), `actividad`, `min_actividad_cumplida`.
- Rango de fechas solo cuando `rol_vista=admin`.
El service filtra según el rol del usuario autenticado:
- TUTOR/PROFESOR: scope automático a sus asignaciones mediante `asignacion_id`.
- COORDINADOR/ADMIN: scope todo el tenant (con rango fechas extra para ADMIN).
**Rationale**: Un solo endpoint evita duplicación. Los filtros se resuelven en SQL vía WHERE dinámico. El guard `atrasados:ver` + verificación de scope resuelve autorización.

### D-06: Nuevo permiso `atrasados:ver` + seed en migración
**Context**: Todos los endpoints del módulo necesitan el permiso `atrasados:ver`.
**Decision**: Se agrega `atrasados:ver` al catálogo de permisos. En la matriz por defecto: TUTOR, PROFESOR, COORDINADOR, ADMIN lo tienen habilitado (scope `propio` para TUTOR/PROFESOR, global para COORDINADOR/ADMIN). Se añade a la migración seed de permisos existente.
**Rationale**: Sigue el patrón de permisos finos establecido en C-04. El seed se actualiza en la migración existente (no se crea migración nueva para un permiso adicional).

### D-07: Nuevas acciones de auditoría
**Context**: Exportaciones y consultas de monitor deben quedar registradas.
**Decision**: Se agregan los códigos `ANALISIS_EXPORTAR` y `ANALISIS_CONSULTAR` al catálogo de auditoría. El service de análisis recibe el helper de auditoría por inyección de dependencia y lo invoca en las operaciones relevantes.
**Rationale**: Consistente con el patrón de C-10 (`CALIFICACIONES_IMPORTAR`).

## Risks / Trade-offs

- **Rendimiento en monitores sin filtros**: Consultar todas las calificaciones del tenant sin filtros de materia puede ser lento en tenants grandes (10k+ alumnos). → Mitigación: los filtros mínimo requeridos son materia o búsqueda textual; no se permite query sin filtro.
- **Atrasados no considera fecha de vencimiento de actividad**: RN-06 define "atrasado = actividad faltante" sin considerar si la actividad ya venció. → Aceptado por ahora; si el negocio requiere ventana temporal, se agrega en iteración futura.
- **Nota final agrupada = promedio simple**: No considera ponderaciones distintas por actividad. → Aceptado por simplicidad; si el negocio requiere ponderaciones, se agrega schema de configuración de pesos.
- **Sin caché**: Cada consulta de monitor ejecuta queries SQL en tiempo real. → Aceptado para este change; si la demanda lo justifica, una capa de caché (Redis) se agrega post-MVP.
