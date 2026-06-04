## Why

Con las calificaciones importadas (C-10) y los umbrales configurados (F2.1), el sistema aún no puede responder preguntas críticas del docente: ¿qué alumnos están en riesgo académico?, ¿cómo se rankean por desempeño?, ¿qué entregas están pendientes de corrección? Sin estas capacidades, la plataforma es solo un repositorio de notas sin valor analítico. C-11 cierra esa brecha agregando la capa de análisis, reportes y monitores que transforma datos crudos en información accionable para tutores, profesores, coordinadores y administración.

## What Changes

- Cómputo de **alumnos atrasados** (F2.2): detecta alumnos con actividades faltantes o nota inferior al umbral configurado (RN-06), usando datos de `Calificacion` + `EntradaPadron`.
- **Ranking de actividades aprobadas** (F2.3): tabla ordenada por cantidad de actividades aprobadas por alumno, excluye alumnos sin ninguna aprobada (RN-09).
- **Reportes rápidos por materia** (F2.4): métricas clave consolidadas (total alumnos, atrasados, actividades detectadas, aprobaciones, tendencias).
- **Notas finales agrupadas** (F2.5): agrupa actividades configuradas, calcula nota final por alumno, lista para exportar o registrar.
- **Exportar trabajos prácticos sin corregir** (F2.6): archivo descargable con entregas detectadas como pendientes de corrección (RN-07, RN-08).
- **Monitores de seguimiento** (F2.7, F2.8, F2.9): vistas filtrables del estado de actividades de los alumnos:
  - Monitor general (COORDINADOR, ADMIN): transversal a todo el tenant.
  - Monitor tutor/profesor (TUTOR, PROFESOR): filtrado por alumnos asignados al usuario.
  - Monitor coordinación/admin con rango de fechas (COORDINADOR, ADMIN).
- Nuevo permiso `atrasados:ver` para todos los endpoints del módulo.
- Nuevos endpoints bajo `/api/analisis/*`.
- Audit log para exportaciones y consultas significativas.

## Capabilities

### New Capabilities
- `analisis-atrasados`: Cómputo de alumnos atrasados por materia (RN-06), ranking de aprobados (RN-09), reportes rápidos, notas finales agrupadas, monitores de seguimiento y exportación de TPs sin corregir.

### Modified Capabilities
<!-- No existing spec files are modified — this change introduces a new capability -->

## Impact

- **New router**: `routers/analisis.py` — endpoints `/api/analisis/*`.
- **New services**: `services/analisis.py` — lógica de atrasados, ranking, notas finales, monitores.
- **New repositories**: `repositories/analisis.py` — queries agregadas sobre `Calificacion`, `EntradaPadron`, `UmbralMateria`.
- **New permission**: `atrasados:ver` — debe agregarse al catálogo de permisos y a la matriz de roles (seed migration).
- **Audit log extensions**: nuevas acciones `ANALISIS_EXPORTAR`, `ANALISIS_CONSULTAR`.
- **No migration needed**: no se crean nuevas tablas; toda la lógica opera sobre datos existentes (`Calificacion`, `EntradaPadron`, `Materia`, `UmbralMateria`, `Asignacion`).
