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

- [ ] Permitir cargar/importar un reporte LMS de finalizacion.
- [ ] Cruzar el reporte LMS con las calificaciones importadas.
- [ ] Listar posibles TPs sin corregir.
- [ ] Agrupar o permitir lectura clara por actividad.
- [ ] Filtrar los resultados.
- [ ] Exportar la tabla resultante.
- [ ] Mostrar confirmacion clara si no hay pendientes.
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

- [ ] Materia o contexto de materia/comision sobre el que se carga el reporte.
- [ ] Cohorte asociada al reporte.
- [ ] Archivo LMS de finalizacion en formato estandar.
- [ ] Estado de carga: cargando, error, exito y sin pendientes.

### Listado

- [x] Alumno.
- [x] Actividad.
- [x] Materia.
- [x] Fecha de entrega o fecha academica asociada.
- [x] Dias pendiente.
- [x] Comision o contexto operativo legible, si aplica.
- [ ] Agrupacion por actividad, como pide HU-02.
- [ ] Total de resultados visibles.

## Importar reporte LMS

- [ ] La pantalla debe permitir subir el reporte LMS de finalizacion.
- [x] Existe backend para importar reporte en `POST /api/calificaciones/completion-report`.
- [ ] El frontend de esta pantalla todavia no usa ese endpoint.
- [ ] El formulario debe pedir materia y cohorte de forma explicita o derivarlos de un contexto claro.
- [ ] Los errores de formato o negocio deben mostrarse con Toast y mensaje accionable.
- [ ] Si no hay pendientes, debe mostrarse una confirmacion clara, no un error.

## Listado

- [x] La pantalla consume datos reales desde `GET /api/entregas/pendientes`.
- [x] La tabla tiene estado vacio: "No hay entregas pendientes de correccion".
- [x] La tabla es responsive con `overflow-x-auto`.
- [x] El filtro por "ID de comision" fue reemplazado por filtro legible por comision.
- [x] El filtro debe ser legible: materia, actividad, alumno, comision o selector disponible.
- [ ] El listado debe agruparse por actividad o, como minimo, ordenar y presentar actividad como eje principal.
- [x] Debe evitar mostrar datos fuera del alcance del usuario autenticado.
- [ ] Debe mostrar errores de carga con Toast compartido.

## Exportacion

- [x] Existe accion de exportar desde frontend.
- [x] Existe backend `GET /api/entregas/pendientes/exportar`.
- [x] La exportacion debe respetar los mismos filtros visibles.
- [ ] Debe mostrar Toast de exito y error.
- [ ] El nombre del archivo debe ser claro para el usuario.

## UX/UI esperada

- [x] Respetar criterios transversales en `revisiones/criterios-transversales-ux-ui.md`.
- [x] No dejar logs de debug en consola.
- [ ] Usar Toast compartido para errores y exitos, con cierre automatico a los 5 segundos.
- [ ] No usar `alert`, `confirm` ni prompts nativos del navegador.
- [ ] Boton de exportar con icono y texto o tooltip claro.
- [ ] Estados de loading, vacio y error claros.
- [ ] Formulario de importacion con controles legibles y validaciones antes de enviar.
- [ ] No mostrar UUID ni IDs tecnicos cuando exista nombre legible.

## Reglas de negocio

- [x] RN-08: el backend de listado considera solo actividades textuales al construir pendientes.
- [x] RN-07: el backend cruza calificaciones existentes contra actividades textuales para detectar faltantes.
- [ ] La importacion del reporte LMS debe ser parte del flujo visible de la pantalla, no solo un endpoint disponible.
- [ ] Validar que el cruce use reporte de finalizacion LMS real, no solo ausencia de nota global.
- [x] Validar scope por usuario: PROFESOR propio; TUTOR, COORDINADOR y ADMIN segun alcance documental.
- [ ] Toda consulta/exportacion/importacion relevante debe auditarse.
- [ ] La identidad debe salir siempre de la sesion JWT, no de parametros.
- [ ] Todo query debe filtrar por `tenant_id` y excluir soft-deleted.
- [x] Datos de prueba cargados usando flujo de importacion de calificaciones, no SQL manual: `backend/scripts/seed_entregas_sin_corregir_dev.py`.

## Estado actual observado

- [x] La ruta y el menu existen.
- [x] La tabla existe y muestra datos reales.
- [x] La exportacion existe.
- [x] El backend tiene logica parcial para RN-07/RN-08.
- [x] Permisos de listado/exportacion alineados entre SRS, frontend y backend.
- [x] Hay datos de prueba disponibles para validar la pantalla: 9 pendientes en `Programacion I`, actividad `Trabajo Final`.
- [ ] Falta carga de reporte LMS en la pantalla.
- [x] Alcance propio/global por rol resuelto para listado y exportacion.
- [ ] Falta UX de Toast para errores/exitos.
- [x] Logs de debug removidos del frontend.
- [x] El filtro por ID de comision fue reemplazado por filtro legible por comision.

## Pendientes para resolver en orden

1. [x] Alinear permisos de backend con `atrasados:ver` o documentar formalmente otro permiso si corresponde.
2. [x] Definir y aplicar alcance por rol para profesor/tutor/coordinador/admin.
3. [ ] Agregar carga de reporte LMS en la pantalla.
4. [x] Mejorar filtros para que sean legibles y no dependan de IDs tecnicos.
5. [ ] Agrupar u ordenar el listado por actividad.
6. [ ] Aplicar Toast compartido para errores/exitos de carga, listado y exportacion.
7. [x] Quitar logs de debug.
8. [ ] Validar auditoria de consulta, exportacion e importacion.
