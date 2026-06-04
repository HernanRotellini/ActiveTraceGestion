## 1. Modelos y Migración

- [x] 1.1 Crear modelo `Calificacion` (id, tenant_id, entrada_padron_id, materia_id, actividad, nota_numerica nullable, nota_textual nullable, aprobado, origen enum Importado|Manual, importado_at, created_at, updated_at, deleted_at)
- [x] 1.2 Crear modelo `UmbralMateria` (id, tenant_id, asignacion_id, materia_id, umbral_pct default 60, valores_aprobatorios JSONB, created_at, updated_at, deleted_at)
- [x] 1.3 Crear migración Alembic 00N: tablas `calificacion` y `umbral_materia`, con FK a materia, entrada_padron, asignacion; unique constraint (tenant_id, materia_id, entrada_padron_id, actividad) en calificacion; unique constraint (tenant_id, asignacion_id, materia_id) en umbral_materia
- [x] 1.4 Agregar permiso `calificaciones:importar` al seed de permisos (rol PROFESOR `(propio)`, rol COORDINADOR global)

## 2. Repositorios

- [x] 2.1 Crear `CalificacionRepository` con scope tenant: métodos `list_by_materia(tenant_id, materia_id)`, `get_by_id`, `create_batch(entries)`, `soft_delete_by_materia(tenant_id, materia_id, usuario_id)`, `count_by_materia`
- [x] 2.2 Crear `UmbralMateriaRepository` con scope tenant: métodos `get_by_asignacion(tenant_id, asignacion_id, materia_id)`, `upsert(tenant_id, data)`, `delete`
- [x] 2.3 Crear `UmbralMateriaRepository.get_default()` que retorna umbral_pct=60 y valores_aprobatorios=["Satisfactorio", "Supera lo esperado"] cuando no hay registro

## 3. Schemas Pydantic

- [x] 3.1 Crear `CalificacionCreate` (entrada_padron_id, materia_id, actividad, nota_numerica? float, nota_textual? str), `CalificacionResponse` (incluye aprobado, origen), `CalificacionListResponse`
- [x] 3.2 Crear `UmbralMateriaCreate` (umbral_pct int, valores_aprobatorios list[str]), `UmbralMateriaResponse`, `UmbralMateriaUpdate`
- [x] 3.3 Crear `ImportPreviewResponse` (actividades detectadas numéricas y textuales, total_rows, sample_rows), `ImportConfirmRequest` (preview_token, actividad_ids seleccionados)
- [x] 3.4 Crear `CompletionReportResponse` (posibles_entregas_sin_corregir: list de {alumno, actividad})

## 4. Servicio de Calificaciones

- [x] 4.1 Implementar `CalificacionService.importar_grades(tenant_id, usuario_id, materia_id, cohorte_id, file)` — flujo completo: parsear archivo, detectar columnas, matchear contra padrón activo, devolver preview
- [x] 4.2 Implementar `CalificacionService.confirmar_import(tenant_id, usuario_id, preview_token, actividad_ids)` — persiste Calificacion records con `origen=Importado`, deriva `aprobado`
- [x] 4.3 Implementar lógica de derivación `_derivar_aprobado(nota_numerica, nota_textual, umbral)` — si numérica: nota >= umbral_pct; si textual: nota_textual in valores_aprobatorios
- [x] 4.4 Implementar matching de alumnos contra `EntradaPadron` activa: lookup por email, luego por nombre+apellido compuesto; los no matcheados se reportan aparte
- [x] 4.5 Implementar `CalificacionService.importar_completion_report(tenant_id, usuario_id, materia_id, cohorte_id, file)` — parsea archivo de finalización, cruza con Calificacion existentes, devuelve lista de posibles entregas sin corregir (solo textuales, RN-08)

## 5. Servicio de Umbral

- [x] 5.1 Implementar `UmbralMateriaService.obtener(tenant_id, asignacion_id, materia_id)` — devuelve el umbral configurado o el default
- [x] 5.2 Implementar `UmbralMateriaService.configurar(tenant_id, asignacion_id, materia_id, data)` — crea o actualiza el UmbralMateria

## 6. Routers

- [x] 6.1 Crear `api/v1/routers/calificaciones.py` con endpoints:
  - `POST /api/calificaciones/import/preview` — subir archivo, obtener preview (guard `calificaciones:importar`)
  - `POST /api/calificaciones/import/confirm` — confirmar import con preview_token y activity_ids
  - `POST /api/calificaciones/completion-report` — subir reporte de finalización, obtener entregas sin corregir
  - `GET /api/calificaciones/umbral?materia_id=X` — obtener umbral configurado
  - `PUT /api/calificaciones/umbral?materia_id=X` — configurar/actualizar umbral
  - `GET /api/calificaciones?materia_id=X` — listar calificaciones de una materia
- [x] 6.2 Registrar router en `app/main.py`

## 7. File Parser

- [x] 7.1 Implementar `LMSFileParser.parse(file)` — detecta formato (xlsx/csv), extrae header row, identifica columnas de identificación (nombre, apellido, email) y columnas de actividad
- [x] 7.2 Implementar `LMSFileParser._detect_column_type(header)` — retorna `numeric` si header termina en `(Real)`, `textual` en caso contrario, `identity` si es columna de identificación del alumno

## 8. Tests

- [x] 8.1 Test: derivación de `aprobado` — numérica >= umbral → true; numérica < umbral → false; textual en conjunto aprobatorio → true; textual fuera → false; sin umbral configurado usa default 60
- [x] 8.2 Test: import preview — archivo válido con columnas mixtas devuelve actividades detectadas correctamente
- [x] 8.3 Test: import confirm — persiste calificaciones con aprobado derivado y origen=Importado
- [x] 8.4 Test: alumnos no matcheados se reportan sin crear registros
- [x] 8.5 Test: completion report — detecta textual sin calificar, ignora numérica sin calificar (RN-08), ignora actividades ya calificadas
- [x] 8.6 Test: umbral por asignación — teacher A configures 70, teacher B uses default 60, same materia
- [x] 8.7 Test: tenant isolation — tenant A no ve calificaciones ni umbral de tenant B
- [x] 8.8 Test: audit trail — import genera `CALIFICACIONES_IMPORTAR` con actor, materia, activity count

## 9. Tareas Finales

- [x] 9.1 Verificar que `calificaciones:importar` permiso esté asignado a PROFESOR `(propio)` y COORDINADOR en el seed
- [x] 9.2 Ejecutar `pytest` y verificar cobertura ≥80% líneas, ≥90% reglas de negocio
- [x] 9.3 Ejecutar lint y typecheck
