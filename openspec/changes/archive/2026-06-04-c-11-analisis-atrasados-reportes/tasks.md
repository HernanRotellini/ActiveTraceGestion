## 1. Seed y permisos

- [x] 1.1 Agregar permiso `atrasados:ver` al catálogo de permisos (seed en migración existente)
- [x] 1.2 Asignar `atrasados:ver` a roles TUTOR, PROFESOR (scope `propio`), COORDINADOR, ADMIN (scope global) en la matriz de rol_permiso
- [x] 1.3 Agregar `ANALISIS_EXPORTAR` y `ANALISIS_CONSULTAR` al catálogo de acciones de auditoría

## 2. Repositorio de análisis

- [x] 2.1 Crear `repositories/analisis.py` con query para listar alumnos atrasados por materia (cruce padrón activo vs calificaciones, detecta faltantes y nota < umbral, RN-06)
- [x] 2.2 Implementar query de ranking de actividades aprobadas con HAVING COUNT y filtro RN-09 (excluye sin aprobadas)
- [x] 2.3 Implementar query de reportes rápidos por materia (métricas consolidadas + desglose por actividad)
- [x] 2.4 Implementar query de notas finales agrupadas (promedio de actividades seleccionadas por alumno)
- [x] 2.5 Implementar query de detección de TPs sin corregir (textual-scale activities sin Calificacion, RN-07/08)
- [x] 2.6 Implementar query de monitor general con filtros dinámicos (materia, regional, comision, busqueda, actividad, min_actividad_cumplida, paginación)
- [x] 2.7 Implementar query de monitor con scope de usuario (filtra por asignaciones del TUTOR/PROFESOR autenticado)
- [x] 2.8 Implementar query de monitor con rango de fechas (filtra Calificacion por importado_at)

## 3. Servicio de análisis

- [x] 3.1 Crear `services/analisis.py` con métodos que orquestan los repositorios y aplican lógica de negocio
- [x] 3.2 Implementar `compute_atrasados()`: recibe materia_id, retorna lista de alumnos atrasados con detalle por actividad
- [x] 3.3 Implementar `compute_ranking()`: recibe materia_id, retorna ranking ordenado descendente
- [x] 3.4 Implementar `compute_reportes_rapidos()`: recibe materia_id, retorna métricas consolidadas
- [x] 3.5 Implementar `compute_notas_finales()`: recibe materia_id + lista de actividades, retorna promedios por alumno
- [x] 3.6 Implementar `compute_tps_sin_corregir()`: recibe materia_id, retorna listado de entregas pendientes
- [x] 3.7 Implementar `get_monitor()`: recibe filtros + usuario autenticado, resuelve scope y retorna datos paginados
- [x] 3.8 Implementar autorización de scope en service: TUTOR/PROFESOR limitado a propias asignaciones, COORDINADOR/ADMIN global
- [x] 3.9 Integrar audit helper en exportaciones (`ANALISIS_EXPORTAR`) y consultas admin (`ANALISIS_CONSULTAR`)

## 4. Router de análisis

- [x] 4.1 Crear `routers/analisis.py` con prefijo `/api/analisis` y guard `require_permission("atrasados:ver")`
- [x] 4.2 Implementar `GET /api/analisis/atrasados/{materia_id}` — retorna lista de alumnos atrasados
- [x] 4.3 Implementar `GET /api/analisis/ranking/{materia_id}` — retorna ranking de aprobados
- [x] 4.4 Implementar `GET /api/analisis/reportes/{materia_id}` — retorna reportes rápidos
- [x] 4.5 Implementar `GET /api/analisis/notas-finales/{materia_id}` — acepta query param `actividades` (CSV de nombres), retorna notas finales agrupadas
- [x] 4.6 Implementar `GET /api/analisis/exportar-tps/{materia_id}` — retorna CSV descargable con TPs sin corregir (StreamingResponse)
- [x] 4.7 Implementar `GET /api/analisis/monitor` — endpoint unificado con filtros query y scope según rol autenticado
- [x] 4.8 Registrar router en `app/main.py`

## 5. Tests

- [x] 5.1 Test: alumno atrasado por actividad faltante (RN-06) — ok
- [x] 5.2 Test: alumno atrasado por nota insuficiente — ok
- [x] 5.3 Test: alumno con todo aprobado NO aparece en atrasados — ok
- [x] 5.4 Test: ranking excluye alumnos sin aprobadas (RN-09) — ok
- [x] 5.5 Test: ranking ordena descendente y alfabético en empate — ok
- [x] 5.6 Test: notas finales agrupadas con promedio de actividades seleccionadas — ok
- [x] 5.7 Test: notas finales excluyen textual-scale activities del promedio — ok
- [x] 5.8 Test: exportar TPs sin corregir excluye actividades numéricas (RN-08) — ok
- [x] 5.9 Test: exportar TPs sin corregir excluye actividades ya calificadas — ok
- [x] 5.10 Test: monitor general con filtro de materia — ok
- [x] 5.11 Test: monitor con búsqueda textual — ok
- [x] 5.12 Test: monitor con paginación — ok
- [x] 5.13 Test: monitor de TUTOR scoped a sus asignaciones — ok
- [x] 5.14 Test: monitor con rango de fechas — ok
- [x] 5.15 Test: 403 sin permiso `atrasados:ver` — ok
- [x] 5.16 Test: aislamiento multi-tenant — ok
- [x] 5.17 Test: exportación genera audit log — ok
- [x] 5.18 Test: reporte rápido con datos vacíos retorna estado informativo — ok
