## 1. Modelos y Migración

- [x] 1.1 Crear modelos `VersionPadron` y `EntradaPadron` en `backend/app/models/padron.py` con campos según E6, `email` cifrado, soft delete, tenant isolation
- [x] 1.2 Agregar modelos al `__init__.py` de models
- [x] 1.3 Crear migración Alembic `version_padron` y `entrada_padron` con índices y FK

## 2. Schemas Pydantic

- [x] 2.1 Crear schemas en `backend/app/schemas/padron.py`:
  - `VersionPadronResponse`, `VersionPadronList`
  - `EntradaPadronResponse`, `EntradaPadronList`
  - `ImportPreviewResponse` (columnas detectadas, sample rows, total)
  - `ImportConfirmRequest` (preview token)
  - `ImportConfirmResponse` (version_id, entry_count)
  - `VaciarResponse` (affected_count)
- [x] 2.2 Agregar schemas al `__init__.py` de schemas

## 3. Repositorio

- [x] 3.1 Crear `PadronRepository` en `backend/app/repositories/padron.py`:
  - `crear_version(materia_id, cohorte_id, cargado_por)` → crea nueva version y desactiva anterior
  - `agregar_entradas(version_id, entries[])` → bulk insert de EntradaPadron
  - `obtener_version_activa(materia_id, cohorte_id)` → consulta con filtro activa=true
  - `obtener_versiones(materia_id, paginado)` → listar histórico
  - `vaciar_por_usuario(materia_id, usuario_id)` → soft delete scope RN-04
- [x] 3.2 Agregar repositorio al `__init__.py` de repositories

## 4. File Parser (xlsx/csv)

- [x] 4.1 Crear `backend/app/services/file_parser.py`:
  - `parsear_archivo(ruta_archivo)` → detecta formato, columnas, devuelve filas normalizadas
  - Soporte para `.xlsx` (openpyxl) y `.csv` (auto-detect delimiter)
  - Validación de columnas requeridas: nombre, apellidos, email
  - Errores descriptivos por fila malformada
  - Limitar preview a primeras N filas

## 5. Preview Cache

- [x] 5.1 Crear lógica de caché temporal para previews:
  - Almacenar preview en caché en proceso (dict con TTL 30 min)
  - Generar token UUID para cada preview
  - `guardar_preview(token, data)` / `obtener_preview(token)` / `eliminar_preview(token)`

## 6. Servicio de Padrón

- [x] 6.1 Crear `PadronService` en `backend/app/services/padron.py`:
  - `preview_importar(materia_id, cohorte_id, archivo)` → parsea, genera preview token
  - `confirmar_importar(token)` → crea VersionPadron + EntradaPadron batch, activa versión
  - `listar_versiones(materia_id, page, size)` → histórico paginado
  - `vaciar_materia(materia_id)` → soft delete scope (usuario_id, materia_id)
  - Integrar auditoría PADRON_CARGAR en confirmar y vaciar

## 7. Router de Padrón

- [x] 7.1 Crear `backend/app/api/v1/routers/padron.py`:
  - `POST /api/v1/padron/preview` — subir archivo, devolver preview
  - `POST /api/v1/padron/confirmar` — confirmar import con preview token
  - `GET /api/v1/padron/materias/{materia_id}/versiones` — listar histórico
  - `DELETE /api/v1/padron/materias/{materia_id}/vaciar` — vaciar datos propios
- [x] 7.2 Registrar router padron en `main.py`

## 8. Moodle Client

- [x] 8.1 Crear `MoodleClient` en `backend/app/integrations/moodle_ws.py`:
  - Config por tenant (base_url + token)
  - `sync_usuarios(materia_id)` → fetch usuarios desde curso Moodle
  - `sync_actividades(materia_id)` → fetch actividades desde curso Moodle
  - Retry con exponential backoff (3 intentos) para errores transitorios
  - Sin retry para 401/403 (auth failure)
  - Timeout configurable
- [x] 8.2 Agregar al `__init__.py` de integrations

## 9. Servicio y Router de Moodle Sync

- [x] 9.1 Agregar método `sync_desde_moodle(materia_id, cohorte_id)` en PadronService
  - Inyecta MoodleClient opcional
  - Sin credenciales → error descriptivo, fallback a import manual
  - Con credenciales → sync + import como nueva versión
  - Error 502 con reintento
- [x] 9.2 Crear endpoints en `backend/app/api/v1/routers/moodle.py`:
  - `POST /api/v1/moodle/sync/{materia_id}` — sync on-demand
- [x] 9.3 Registrar router de moodle en `main.py`

## 10. Integración con Main

- [x] 10.1 Registrar routers `padron` y `moodle` en `backend/app/main.py`
- [x] 10.2 Agregar dependencia openpyxl y httpx en `pyproject.toml`, moodle opts en config

## 11. Tests

- [x] 11.1 Tests de modelo y migración: versionado (activar desactiva anterior), historial preservado, email cifrado, tenant isolation
- [x] 11.2 Tests de repositorio: CRUD, versionado, vaciar scope RN-04, soft delete
- [x] 11.3 Tests de file parser: xlsx válido, csv con delimitador alternativo, columnas faltantes → 422
- [x] 11.4 Tests de import flow: preview → confirmar → versión activa, preview expirado → 409
- [x] 11.5 Tests de vaciar: solo datos propios, datos de otros docentes preservados
- [x] 11.6 Tests de MoodleClient: sync usuarios, retry transitorio, auth failure inmediato, 502 fallback
- [x] 11.7 Tests de sync on-demand: PROFESOR autorizado, COORDINADOR autorizado, sin permiso → 403, sin credenciales → error descriptivo
