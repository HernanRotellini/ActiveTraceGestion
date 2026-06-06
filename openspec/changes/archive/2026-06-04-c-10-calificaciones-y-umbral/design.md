## Context

Activia-trace necesita poder importar y almacenar calificaciones de alumnos desde archivos exportados del LMS (Moodle). Esto es un prerrequisito para el análisis de atrasados (C-11) y las comunicaciones (C-12). El módulo se apoya en el padrón versionado (C-09) para identificar alumnos destino y en la estructura académica (C-06) para las materias.

Dependencias existentes que este diseño usa:
- `EntradaPadron` (C-09): los alumnos destino vienen de la versión activa del padrón
- `Asignacion` (C-07): el umbral se configura por asignación docente
- `Materia` (C-06): catálogo de materias del tenant
- `AuditLog` (C-05): registro de acciones de importación
- `require_permission` (C-04): guard `calificaciones:importar`

## Goals / Non-Goals

**Goals:**
- Proveer modelo de datos para `Calificacion` y `UmbralMateria`
- Importar calificaciones desde archivo xlsx/csv con vista previa y selección de actividades
- Importar reporte de finalización y detectar entregas sin calificar
- Configurar umbral de aprobación por asignación docente
- Derivar `aprobado` automáticamente según umbral/configuración textual
- Auditoría completa de operaciones de importación
- Aislamiento multi-tenant

**Non-Goals:**
- Cálculo de atrasados (C-11) — se construye sobre este módulo
- Ranking de actividades aprobadas (C-11)
- Notas finales agrupadas (C-11)
- Exportación de datos (cubre importación y configuración solamente)
- Integración directa con Moodle WS para calificaciones (el import es siempre por archivo en esta fase)

## Decisions

### DEC-01: Dos modelos separados (Calificacion + UmbralMateria) en lugar de un solo modelo con configuración embebida

Se separan porque tienen ciclos de vida distintos: las calificaciones se importan y son inmutables (son datos históricos), mientras que el umbral se configura y puede cambiar. Además, `UmbralMateria` se relaciona con `Asignacion` (alcance por docente), mientras que `Calificacion` se relaciona con `EntradaPadron` (alcance por alumno).

### DEC-02: `aprobado` se deriva en escritura (write-time), no en consulta

Derivar en escritura evita recalcular cada vez que se lee, lo que importa dado que las calificaciones se leen frecuentemente para reportes y monitores (C-11). Si el umbral cambia, se pueden recalcular en lote las `aprobado` afectadas. Alternativa considerada: derivar en consulta → descartada por performance en lecturas masivas.

### DEC-03: Preview como token efímero en memoria, no persistido

Sigue el mismo patrón que C-09 (padron-ingesta). El preview se genera, se almacena en un dict en memoria con TTL (ej. 10 min), y se confirma con el token. Alternativa considerada: persistir preview en DB → descartada por complejidad innecesaria (el preview es transitorio).

### DEC-04: Detección de columnas por sufijo `(Real)` para numéricas (RN-01)

Las columnas que terminan en `(Real)` se interpretan como nota numérica. Cualquier otra columna que no sea de identificación del alumno se trata como textual. Esto sigue exactamente el formato de exportación de Moodle.

### DEC-05: Umbral por defecto 60% hardcodeado + valores textuales default en configuración

El tenant puede sobreescribir estos defaults vía su configuración en el futuro. Por ahora, `DEFAULT_UMBRAL_PCT = 60` y `DEFAULT_VALORES_APROBATORIOS = ["Satisfactorio", "Supera lo esperado"]` son constantes del módulo.

## Risks / Trade-offs

- **[Write-time aprobado puede quedar inconsistente si cambia el umbral]** → Mitigación: endpoint de recalculo `/api/calificaciones/recalcular` que actualiza `aprobado` para todas las calificaciones de una materia donde el umbral cambió.
- **[Archivos LMS con formatos no estándar]** → Mitigación: el preview muestra claramente qué columnas se detectan como numéricas/textuales; el usuario selecciona cuáles incluir. Si una columna no se detecta correctamente, el usuario simplemente no la selecciona.
- **[Matching de alumnos por nombre/apellido/email puede fallar]** → Mitigación: los alumnos no matcheados se reportan separadamente en el preview, y no se importan. El usuario puede corregir el padrón antes de confirmar.
