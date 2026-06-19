# Checklist - Pantalla Entregas sin Corregir

## Fuentes revisadas

- `docs/PRD.md`: RF-16 pide deteccion de TP entregados sin corregir, filtrable y exportable, asociado a HU-02.
- `docs/SRS.md`: `/docente/entregas` requiere `atrasados:ver`, muestra actividades/alumnos posiblemente pendientes y permite filtrar/exportar.
- `knowledge-base/11_historias_de_usuario.md`: HU-02 pide que PROFESOR suba reporte LMS de finalizacion para detectar trabajos entregados pero no corregidos.
- `knowledge-base/06_funcionalidades.md`: F1.2 pide importar reporte de finalizacion LMS; F2.6 pide exportar trabajos practicos sin corregir.
- `knowledge-base/07_flujos_principales.md`: el sistema cruza el reporte de finalizacion LMS con las calificaciones importadas.
- `knowledge-base/05_reglas_de_negocio.md`: RN-07 y RN-08 definen la deteccion y limitan el resultado a actividades de escala textual.
- `knowledge-base/03_actores_y_roles.md`: pueden detectar entregas sin corregir TUTOR, PROFESOR propio, COORDINADOR y ADMIN.

## Alcance esperado

- [x] Permitir cargar/importar un reporte LMS de finalizacion.
- [x] Cruzar el reporte LMS con las calificaciones importadas.
- [x] Listar posibles TPs sin corregir.
- [x] Agrupar o permitir lectura clara por actividad.
- [x] Filtrar los resultados.
- [x] Exportar la tabla resultante.
- [x] Mostrar confirmacion clara si no hay pendientes.
- [x] Respetar alcance por rol: PROFESOR sobre lo propio; TUTOR, COORDINADOR y ADMIN sobre el alcance completo del tenant, segun matriz documental.

## Permisos esperados

- [x] Frontend protege `/docente/entregas` con `atrasados:ver`, segun `docs/SRS.md`.
- [x] El menu lateral muestra `Entregas sin corregir` solo con `atrasados:ver`.
- [x] Backend `/api/entregas/pendientes` usa `atrasados:ver`, alineado con `docs/SRS.md`.
- [x] Backend `/api/entregas/pendientes/exportar` usa `atrasados:ver`, alineado con `docs/SRS.md`.
- [x] Se detecto que existe un permiso sembrado `entregas:detectar_sin_corregir`, pero los documentos de ruta/flujo piden `atrasados:ver`; no se usa para esta pantalla por ahora.
- [ ] La carga del reporte LMS debe tener permiso documentado y coherente con HU-02/SRS; hoy existe en `/api/calificaciones/completion-report` bajo guard de calificaciones.
- [x] PROFESOR no debe ver entregas de materias/comisiones ajenas.
- [x] TUTOR, COORDINADOR y ADMIN pueden consultar dentro del alcance permitido por tenant y permisos.

## Campos esperados

### Entrada / importacion

- [x] Materia o contexto de materia/comision sobre el que se carga el reporte.
- [x] Cohorte asociada al reporte.
- [x] Archivo LMS de finalizacion en formato estandar.
- [x] Estado de carga: cargando, error, exito y sin pendientes.

### Listado

- [x] Alumno.
- [x] Actividad.
- [x] Materia.
- [x] Fecha de entrega o fecha academica asociada.
- [x] Dias pendiente.
- [x] Comision o contexto operativo legible, si aplica.
- [x] Agrupacion por actividad, como pide HU-02.
- [x] Total de resultados visibles.

## Importar reporte LMS

- [x] La pantalla debe permitir subir el reporte LMS de finalizacion.
- [x] Existe backend para importar reporte en `POST /api/calificaciones/completion-report`.
- [x] El frontend de esta pantalla ya usa ese endpoint (componente `ImportarReporteLms`).
- [x] El formulario debe pedir materia y cohorte de forma explicita o derivarlos de un contexto claro.
- [x] Los errores de formato o negocio deben mostrarse con Toast y mensaje accionable.
- [x] Si no hay pendientes, debe mostrarse una confirmacion clara, no un error.

## Listado

- [x] La pantalla consume datos reales desde `GET /api/entregas/pendientes`.
- [x] La tabla tiene estado vacio: "No hay entregas pendientes de correccion".
- [x] La tabla es responsive con `overflow-x-auto`.
- [x] El filtro por "ID de comision" fue reemplazado por filtro legible por comision.
- [x] El filtro debe ser legible: materia, actividad, alumno, comision o selector disponible.
- [x] El listado debe agruparse por actividad o, como minimo, ordenar y presentar actividad como eje principal.
- [x] Debe evitar mostrar datos fuera del alcance del usuario autenticado.
- [x] Debe mostrar errores de carga con Toast compartido.

## Exportacion

- [x] Existe accion de exportar desde frontend.
- [x] Existe backend `GET /api/entregas/pendientes/exportar`.
- [x] La exportacion debe respetar los mismos filtros visibles.
- [x] Debe mostrar Toast de exito y error.
- [x] El nombre del archivo debe ser claro para el usuario (`entregas-sin-corregir-AAAA-MM-DD.csv`, ahora con descarga real).

## UX/UI esperada

- [x] Respetar criterios transversales en `revisiones/criterios-transversales-ux-ui.md`.
- [x] No dejar logs de debug en consola.
- [x] Usar Toast compartido para errores y exitos, con cierre automatico a los 5 segundos.
- [x] No usar `alert`, `confirm` ni prompts nativos del navegador.
- [x] Boton de exportar con icono y texto o tooltip claro.
- [x] Estados de loading, vacio y error claros.
- [x] Formulario de importacion con controles legibles y validaciones antes de enviar.
- [x] No mostrar UUID ni IDs tecnicos cuando exista nombre legible.

## Reglas de negocio

- [x] RN-08: el backend de listado considera solo actividades textuales al construir pendientes.
- [x] RN-07: el backend cruza calificaciones existentes contra actividades textuales para detectar faltantes.
- [x] La importacion del reporte LMS debe ser parte del flujo visible de la pantalla, no solo un endpoint disponible.
- [ ] Validar que el cruce use reporte de finalizacion LMS real, no solo ausencia de nota global. (El flujo de importacion ya usa el reporte LMS real via `completion-report`; el listado principal `/entregas/pendientes` sigue derivando de ausencia de nota textual RN-07/08 — definir si debe condicionarse al reporte importado.)
- [x] Validar scope por usuario: PROFESOR propio; TUTOR, COORDINADOR y ADMIN segun alcance documental.
- [x] Toda consulta/exportacion/importacion relevante debe auditarse. (Bug de auditoria corregido en `AnalisisService._registrar_auditoria`; consulta y exportacion de entregas ahora persisten en `audit_log`. Cubierto por tests `TestAuditoriaEntregasPendientes` en `backend/tests/test_analisis.py`.)
- [x] La identidad debe salir siempre de la sesion JWT, no de parametros. (Verificado: routers usan `current_user` de la sesion, nunca params.)
- [x] Todo query debe filtrar por `tenant_id` y excluir soft-deleted. (Verificado en `AnalisisRepository.entregas_pendientes`: filtra `tenant_id` y `deleted_at IS NULL`.)
- [x] Datos de prueba cargados usando flujo de importacion de calificaciones, no SQL manual: `backend/scripts/seed_entregas_sin_corregir_dev.py`.

## Estado actual observado

- [x] La ruta y el menu existen.
- [x] La tabla existe y muestra datos reales.
- [x] La exportacion existe.
- [x] El backend tiene logica parcial para RN-07/RN-08.
- [x] Permisos de listado/exportacion alineados entre SRS, frontend y backend.
- [x] Hay datos de prueba disponibles para validar la pantalla: 9 pendientes en `Programacion I`, actividad `Trabajo Final`.
- [x] Carga de reporte LMS agregada a la pantalla (`ImportarReporteLms`).
- [x] Alcance propio/global por rol resuelto para listado y exportacion.
- [x] UX de Toast para errores/exitos aplicada (carga, listado, exportacion e importacion).
- [x] Logs de debug removidos del frontend.
- [x] El filtro por ID de comision fue reemplazado por filtro legible por comision.

## Pendientes para resolver en orden

1. [x] Alinear permisos de backend con `atrasados:ver` o documentar formalmente otro permiso si corresponde.
2. [x] Definir y aplicar alcance por rol para profesor/tutor/coordinador/admin.
3. [x] Agregar carga de reporte LMS en la pantalla.
4. [x] Mejorar filtros para que sean legibles y no dependan de IDs tecnicos.
5. [x] Agrupar u ordenar el listado por actividad.
6. [x] Aplicar Toast compartido para errores/exitos de carga, listado y exportacion.
7. [x] Quitar logs de debug.
8. [x] Validar auditoria de consulta, exportacion e importacion. (Bug corregido y verificado con tests; ver "Hallazgo critico — RESUELTO".)

## Hallazgo critico — RESUELTO (dominio CRITICO: audit log, corregido con aprobacion del usuario)

`AnalisisService._registrar_auditoria` (`backend/app/services/analisis.py`) **nunca persistia auditoria**:

- Importaba `from app.models.audit import AuditLog`, pero el modelo real es `app.models.audit_log.AuditLog` → siempre lanzaba `ImportError`.
- Construia `AuditLog(recurso_id=..., recurso_tipo=...)`, columnas que **no existen** en el modelo (el modelo tiene `materia_id`, `accion`, `detalle`, `filas_afectadas`, `ip`, `user_agent`).
- Todo estaba envuelto en `except (ImportError, Exception): pass`, asi que la falla se tragaba en silencio.

Efecto (antes del fix): el listado y la exportacion de entregas sin corregir (y el resto de metodos de `AnalisisService`) **no generaban registro de auditoria**, incumpliendo RN-23.

**Correccion aplicada** (con aprobacion explicita del usuario, dominio CRITICO):
- Import corregido a `app.models.audit_log.AuditLog` (a nivel de modulo).
- `_registrar_auditoria` mapea a las columnas reales (`tenant_id`, `actor_id`, `materia_id`, `accion`, `detalle`); identidad siempre desde la sesion.
- Se elimino el `except ... : pass` que tragaba errores; la entrada queda en la unit-of-work y se persiste con el commit del request (`get_db`).
- Tests TDD sin mock de DB (Postgres efimero): `TestAuditoriaEntregasPendientes` en `backend/tests/test_analisis.py` (consulta → `ANALISIS_CONSULTAR`; exportacion → `ANALISIS_EXPORTAR`). **2 passed.**

> Nota: el fix corrige `_registrar_auditoria` en su raiz, por lo que tambien repara la auditoria del resto de metodos de `AnalisisService` (atrasados, ranking, reportes, monitor, notas finales). Mejora futura opcional: enriquecer con `ip`/`user_agent` via el `AuditService` central, que requiere propagarlos desde el router.
