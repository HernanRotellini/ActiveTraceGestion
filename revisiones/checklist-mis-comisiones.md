# Checklist - Pantalla Mis Comisiones

## Fuentes revisadas

- `Funcionalidad.md`: `/docente/comisiones` lista las comisiones asignadas al docente y abre un detalle con calificaciones, importar notas, umbral, atrasados, ranking, notas finales y reportes.
- `docs/SRS.md`: `/docente/comisiones` requiere `calificaciones:ver`; muestra materias/comisiones asignadas y estado de analisis. `/docente/comisiones/:id` permite gestionar una comision concreta.
- `knowledge-base/06_funcionalidades.md`: el docente ve comisiones y materias asignadas, rol, carrera, cohorte, comisiones asociadas, vigencia y estado.
- `knowledge-base/07_flujos_principales.md`: el profesor selecciona materia/cohorte/comision, importa calificaciones, configura umbral, revisa atrasados, ranking, reportes y notas finales.
- `knowledge-base/04_modelo_de_datos.md`: las comisiones hoy figuran como lista de texto dentro de `Asignacion`.
- `knowledge-base/10_preguntas_abiertas.md`: PA-01 deja pendiente separar formalmente Materia de instancia de dictado/comision. Hasta que se cierre, esta pantalla debe trabajar con asignaciones y comisiones asociadas.

## Alcance esperado

- [ ] Listar solo las materias/comisiones asignadas al usuario logueado.
- [ ] Permitir entrar al detalle de una comision/materia asignada.
- [ ] Mostrar en el detalle las secciones esperadas: calificaciones, importar notas, umbral, atrasados, ranking, notas finales y reportes.
- [ ] No permitir ver ni operar comisiones de otros docentes.
- [ ] Auditar consultas y acciones relevantes segun criterio transversal de auditoria.

## Decision sobre origen de comisiones

- [x] No se encontro en los documentos un ABM independiente donde ADMIN cree un catalogo de comisiones.
- [x] Segun `knowledge-base/11_historias_de_usuario.md` HU-18, las comisiones se informan al asignar docentes a una materia x carrera x cohorte x rol.
- [x] Segun `knowledge-base/04_modelo_de_datos.md`, `Asignacion.comisiones` es una `lista<texto>`, puede ser vacia y no referencia una tabla `Comision`.
- [x] Segun `docs/SRS.md`, una comision es un grupo operativo de cursado dentro de una materia/cohorte, pero `Dictado` figura como decision pendiente de representacion final.
- [x] La pantalla de nueva asignacion de equipos permite cargar comisiones como parte de la asignacion docente. Sin esto, "Mis Comisiones" no podia mostrar datos completos.

**Criterio actual**

- No implementar un ABM nuevo de comisiones mientras no este pedido por documentos.
- Para esta pantalla, usar `Asignacion.comisiones` como fuente de verdad disponible.
- Si una asignacion no tiene comisiones cargadas, mostrar la materia/cohorte asignada y un estado claro: "Sin comisiones cargadas".

## Permisos esperados

- [x] La ruta `/docente/comisiones` esta protegida en frontend con `calificaciones:ver`.
- [x] La ruta `/docente/comisiones/:id` esta protegida en frontend con `calificaciones:ver`.
- [x] El listado real de mis comisiones debe estar protegido en backend con `calificaciones:ver`, segun `docs/SRS.md`.
- [x] Importar calificaciones requiere `calificaciones:importar` en backend.
- [x] Ver calificaciones requiere `calificaciones:ver` en backend.
- [x] Ver atrasados, ranking, notas finales y reportes usa backend `/api/analisis/*` con `atrasados:ver`.
- [x] La UI debe ocultar o bloquear acciones si el usuario no tiene el permiso especifico, por ejemplo importar si no tiene `calificaciones:importar`.

**Estado actual observado**

- [x] El menu lateral muestra `Mis Comisiones` solo con `calificaciones:ver`.
- [x] Las rutas frontend bloquean acceso sin `calificaciones:ver`.
- [x] `backend/app/api/v1/routers/asignaciones.py` expone `GET /api/asignaciones/mis-comisiones` con `calificaciones:ver`.
- [x] El endpoint toma `current_user.user_id` desde la sesion y no acepta `usuario_id` por query/body.
- [x] `backend/app/api/v1/routers/equipos.py` protege `GET /api/equipos/mis-equipos` con `calificaciones:ver`.
- [x] La pestaña de importar se oculta si el usuario no tiene `calificaciones:importar`.
- [ ] No esta listo: el detalle permite entrar por `:id` sin que exista aun una validacion backend especifica de pertenencia de esa asignacion/comision al docente autenticado.

**Decision de implementacion propuesta**

- [x] Crear un endpoint de lectura propia, `GET /api/asignaciones/mis-comisiones`, protegido con `calificaciones:ver`.
- [x] El endpoint usa `current_user.user_id` y `current_user.tenant_id`; no acepta `usuario_id` desde query/body.
- [x] Mantener los endpoints administrativos de asignaciones con permisos de equipos.
- [x] En frontend, ocultar o bloquear la pestaña/accion de importar si falta `calificaciones:importar`.

## Campos esperados

### Listado

- [ ] Materia.
- [ ] Carrera.
- [ ] Cohorte.
- [ ] Comision o comisiones asociadas.
- [ ] Rol ejercido por el usuario en esa asignacion.
- [ ] Vigencia desde / hasta.
- [ ] Estado de la asignacion: vigente, vencida o futura.
- [ ] Estado de analisis: sin datos, importado, con atrasados, actualizado, etc. El nombre exacto no esta definido en documentos, pero SRS pide mostrar estado de analisis.
- [ ] Accion para entrar al detalle.

### Detalle

- [x] Encabezado con materia, carrera, cohorte y comision, no solo el id.
- [x] Datos de la asignacion propia: rol y vigencia.
- [x] Pestaña Calificaciones.
- [x] Pestaña Importar.
- [x] Pestaña Configuracion / Umbral.
- [x] Pestaña Atrasados.
- [x] Pestaña Ranking.
- [x] Pestaña Notas Finales.
- [x] Pestaña Reportes.

## Listado

- [x] Debe consumir datos reales del backend.
- [x] Debe obtener solo asignaciones del usuario autenticado desde la sesion, no desde parametros de URL.
- [x] Debe filtrar por tenant en backend.
- [x] Debe mostrar estado vacio solo cuando realmente no existan asignaciones.
- [x] Debe tener loading y error con Toast compartido.
- [x] Debe permitir buscar o filtrar por estado, materia, rol, carrera y cohorte, segun `F4.2`.

**Estado actual observado**

- [x] `ComisionesListPage.tsx` consume `GET /api/asignaciones/mis-comisiones`.
- [x] El listado muestra materia, carrera, cohorte, rol, comisiones, vigencia, estado y accion de detalle.
- [x] Si una asignacion no tiene comisiones cargadas, muestra "Sin comisiones cargadas".
- [x] Los nombres legibles de carrera/cohorte/materia se resuelven desde el endpoint docente, sin usar endpoints admin.

## Detalle de comision

- [x] Existe la pantalla `/docente/comisiones/:id`.
- [x] Existen tabs visuales para todas las secciones esperadas.
- [x] El detalle debe resolver el contexto real de la comision/materia/asignacion antes de consultar datos.
- [x] El titulo debe mostrar informacion legible, no `Comision {id}`.
- [x] Si el id no pertenece al docente autenticado, backend debe responder 403 o 404 sin filtrar datos.

**Estado actual observado**

- [x] `GET /api/asignaciones/mis-comisiones/{id}` valida la asignacion contra el usuario de la sesion.
- [x] El frontend usa `id` como `asignacion_id` y desde ahi obtiene `materia_id`, `cohorte_id`, `carrera_id`, rol, comisiones y vigencia.
- [x] Las pestañas usan los endpoints reales de calificaciones y analisis.

## Importar calificaciones

- [x] La importacion debe usar `materia_id` y `cohorte_id` del contexto seleccionado.
- [x] Debe subir archivo LMS al endpoint real `/api/calificaciones/import/preview`.
- [x] Debe mostrar actividades detectadas y permitir seleccionar cuales confirmar.
- [x] Debe confirmar en `/api/calificaciones/import/confirm`.
- [x] Los errores deben usar Toast compartido y mensajes accionables.
- [x] Si no hay permisos para importar, la accion debe quedar oculta o bloqueada.

**Estado actual observado**

- [x] El servicio frontend usa `/api/calificaciones/import/preview` y `/api/calificaciones/import/confirm`.
- [x] El formulario usa Toast compartido para exito y error.

## Umbral

- [x] Debe mostrar el umbral actual, con default 60% si no hay configuracion.
- [x] Debe permitir configurar valores aprobatorios y porcentaje.
- [x] Debe usar `materia_id` y `asignacion_id`, como espera el backend.
- [x] Debe mostrar Toast de exito y error.

**Estado actual observado**

- [x] El frontend llama `/api/calificaciones/umbral?materia_id=...&asignacion_id=...`.

## Atrasados, ranking, notas finales y reportes

- [x] Atrasados debe usar `/api/analisis/atrasados/{materia_id}`.
- [x] Ranking debe usar `/api/analisis/ranking/{materia_id}`.
- [x] Notas finales debe usar `/api/analisis/notas-finales/{materia_id}` con actividades.
- [x] Reportes debe usar `/api/analisis/reportes/{materia_id}`.
- [x] La UI debe alinear contratos de respuesta con los schemas reales de backend.
- [x] Debe mostrar loading, vacio y error con criterios transversales.

**Estado actual observado**

- [x] El frontend llama endpoints bajo `/api/analisis/...` para atrasados, ranking, notas finales y reportes.

## UX/UI esperada

- [x] Respetar criterios transversales en `revisiones/criterios-transversales-ux-ui.md`.
- [x] Toast para errores y exitos, con cierre automatico a los 5 segundos.
- [x] No usar `alert`, `confirm` ni prompts nativos del navegador.
- [x] Estados de loading, vacio y error claros.
- [x] Tabs legibles y navegables en mobile.
- [x] Tablas con contenedor responsive para no romper en pantallas chicas.
- [x] Botones de acciones con icono y tooltip cuando corresponda.
- [x] No mostrar textos tecnicos como UUID cuando exista nombre de materia/comision disponible.

**Estado actual observado**

- [x] `Mis Comisiones` y el detalle no usan `alert`, `confirm`, prompts ni `Alert`.
- [x] Importacion y umbral usan `Toast` compartido para exito/error.
- [x] Listado, detalle y tablas muestran estados de loading/vacio.
- [x] Tabs usan `overflow-x-auto` para pantallas chicas.
- [x] Tablas principales usan contenedor responsive.
- [x] Materia, carrera y cohorte se muestran por nombre desde el endpoint docente enriquecido.
- [x] No hay acciones de editar/eliminar en esta pantalla; por eso no aplican iconos de lapiz/tacho.

## Reglas de negocio

- [x] El docente solo opera sus propias asignaciones/comisiones.
- [x] Las asignaciones vigentes se determinan por `desde` y `hasta`.
- [x] La identidad sale siempre de la sesion JWT.
- [x] Todo query debe filtrar por `tenant_id`.
- [x] La importacion debe aplicar RN-01 y RN-02 para detectar actividades y valores reales/textuales.
- [x] El umbral default es 60% segun RN-03.
- [x] Los atrasados se calculan segun RN-06.
- [x] Entregas sin corregir aplica RN-07 y RN-08 cuando corresponda.
- [x] Ranking de actividades aprobadas aplica RN-09.
- [x] Toda accion relevante debe auditarse.

**Estado actual observado**

- [x] `GET /api/asignaciones/mis-comisiones` resuelve el usuario de dominio desde el email de la sesion y filtra por `usuario_id`.
- [x] `GET /api/asignaciones/mis-comisiones/{id}` valida pertenencia antes de devolver el detalle.
- [x] Repositories consultan con `tenant_id` y `deleted_at IS NULL`.
- [x] `AsignacionResponse.estado_vigencia` deriva vigencia por fechas.
- [x] Importacion de calificaciones audita `CALIFICACIONES_IMPORTAR`.
- [x] Consultas de analisis auditan `ANALISIS_CONSULTAR`.
- [x] Configuracion de umbral audita `UMBRAL_CONFIGURAR`.

## Estado actual general

- [x] Pantalla lista funcionalmente.
- [x] La navegacion y proteccion frontend basica existen.
- [x] El backend tiene piezas para calificaciones, umbral y analisis.
- [x] Existe endpoint/servicio claro para "mis comisiones" basado en asignaciones propias.
- [x] Contratos frontend-backend alineados.
- [x] UX/UI adaptada a criterios transversales.

## Pendientes para resolver en orden

1. [x] Permisos y alcance exacto del listado propio.
2. [x] Endpoint backend para listar mis asignaciones/comisiones desde sesion.
3. [x] Reemplazar mock del listado por datos reales.
4. [x] Definir identificador de navegacion del detalle: asignacion, materia+cohorte+comision o futura entidad comision.
5. [x] Alinear servicios frontend con endpoints reales de calificaciones y analisis.
6. [x] Aplicar Toast compartido y estados UX/UI.
7. [x] Validar reglas de negocio y auditoria.
