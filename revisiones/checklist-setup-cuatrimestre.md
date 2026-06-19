# Checklist de revision - Pantalla Setup Cuatrimestre

## Fuentes revisadas

- [x] `Funcionalidad.md`
- [x] `docs/SRS.md`
- [x] `docs/PRD.md`
- [x] `knowledge-base/04_modelo_de_datos.md`
- [x] `knowledge-base/06_funcionalidades.md`
- [x] `knowledge-base/07_flujos_principales.md`
- [x] `knowledge-base/11_historias_de_usuario.md`
- [x] `revisiones/criterios-transversales-ux-ui.md`

Estado:
- `Funcionalidad.md` define esta pantalla como gestion de periodos academicos: crear, activar/desactivar cuatrimestres con fechas de inicio y fin.
- `docs/SRS.md` define la ruta como preparacion de inicio de periodo e incluye periodo/cohorte, equipos a clonar y estructura.
- `FL-03` describe el flujo completo de inicio de cuatrimestre, incluyendo tareas que pertenecen a otros modulos o permisos.
- `HU-23` y SRS separan programas/fechas academicas como funcionalidades propias que pueden aparecer dentro del setup, pero tienen requisitos especificos.

## Alcance esperado

La pantalla `/coordinacion/setup-cuatrimestre` prepara el inicio de un periodo academico. Segun `Funcionalidad.md`, su alcance minimo es gestionar periodos academicos: crear, activar/desactivar cuatrimestres con fechas de inicio y fin.

Segun `docs/SRS.md` y `FL-03`, el flujo completo de setup de cuatrimestre incluye ademas crear/ajustar cohorte, clonar equipos docentes, ajustar vigencias, cargar programas oficiales, registrar fechas academicas, publicar aviso e importar padron inicial. No todo ese flujo necesariamente debe vivir en una sola pantalla.

Alcance funcional esperado para esta revision:
- [x] Gestionar periodos academicos: crear, editar, activar/desactivar y baja tecnica si se expone.
- [x] Registrar fechas academicas asociadas al periodo, revisando si tambien deben asociarse a materia/cohorte.
- [x] Gestionar programas oficiales solo si se respeta HU-23: materia + carrera + cohorte + titulo + archivo PDF/referencia opaca.

Fuera del alcance directo de esta pantalla, salvo decision explicita de producto:
- [x] Clonado real de equipo docente: pertenece a `equipos:asignar`.
- [x] Alta masiva o ajuste de asignaciones docentes: pertenece a equipos/asignaciones.
- [x] Publicacion de avisos: pertenece a avisos.
- [x] Importacion de padron inicial: pertenece a padron/importacion.

Estado:
- La pantalla ahora funciona como hub de setup: periodos, accesos operativos y paneles separados para programas oficiales y fechas academicas.
- La seccion de programas usa el modelo oficial `/api/programas`.
- La seccion de fechas usa `/api/fechas-academicas` con materia, cohorte, tipo, numero, periodo y titulo.

## Permisos esperados

- [x] Definir permiso final de la pantalla segun documentos.
- [x] Deben poder acceder `ADMIN` y `COORDINADOR` si tienen el permiso efectivo.
- [x] El sistema debe resolver acceso por permisos efectivos, no por rol hardcodeado.
- [x] El backend debe validar permisos; la UI no debe ser la unica barrera.

Estado:
- Permiso esperado documental: `estructura:gestionar`, declarado por `docs/SRS.md` para `/coordinacion/setup-cuatrimestre`.
- Implementacion aplicada: ruta frontend, menu y endpoints relevantes del setup validan `estructura:gestionar`.
- El acceso sigue resolviendose por permisos efectivos via `PermissionGuard` y `require_permission(...)`.
- El seed mantiene `periodos:gestionar` legacy, pero ya no es el permiso de acceso efectivo para esta pantalla.

## Campos esperados

- [x] Periodo academico:
  - `nombre`.
  - `fecha_inicio`.
  - `fecha_fin`.
  - `activo`.
- [x] Fecha academica:
  - `periodo_id`.
  - Tipo o clave de fecha.
  - Titulo/etiqueta.
  - Fecha.
  - Asociacion al periodo.
  - Segun SRS/modelo objetivo: asociacion a materia/cohorte cuando aplique.
- [x] Programa:
  - Materia.
  - Carrera.
  - Cohorte.
  - Titulo.
  - Archivo PDF o referencia de archivo opaca.

Estado:
- Periodos usan `nombre`, `fecha_inicio`, `fecha_fin` y `activo`.
- Fechas academicas usan `periodo_id`, `tipo`, `titulo`, `fecha`, `periodo`, `materia_id` y `cohorte_id`.
- Programas oficiales usan `materia_id`, `carrera_id`, `cohorte_id`, `titulo` y `referencia_archivo`.

## Listado

- [x] Listar periodos academicos.
- [x] Mostrar rango de vigencia inicio/fin.
- [x] Mostrar estado activo/inactivo.
- [x] Mostrar fechas academicas del periodo.
- [x] Mostrar programas asociados del periodo si la pantalla mantiene esa seccion.
- [x] No mostrar periodos eliminados por soft delete.
- [x] Mostrar acciones disponibles segun estado y reglas de negocio.

Estado:
- Frontend lista periodos con nombre, rango, estado y acciones.
- La pantalla muestra ademas paneles propios para fechas academicas y programas oficiales dentro del flujo de setup.
- Backend lista por tenant y no deberia mostrar soft deleted.
- Acciones actuales: activar/desactivar, editar, eliminar si inactivo, crear/editar/borrar programas y crear/editar/borrar fechas.

## Crear periodo

- [x] Permitir cargar `nombre`.
- [x] Permitir seleccionar `fecha_inicio`.
- [x] Permitir seleccionar `fecha_fin`.
- [x] Validar campos obligatorios.
- [x] Validar que `fecha_fin >= fecha_inicio`.
- [x] Mostrar mensajes especificos, no genericos.
- [x] Confirmar si el periodo se crea activo o inactivo por defecto.

Estado:
- Frontend valida obligatorios y rango de fechas.
- Backend valida `fecha_fin >= fecha_inicio`.
- El periodo se crea inactivo por defecto segun modelo actual.
- Errores y exitos se muestran con `Toast`.

## Editar periodo

- [x] Permitir editar `nombre`.
- [x] Permitir editar `fecha_inicio`.
- [x] Permitir editar `fecha_fin`.
- [x] Validar que `fecha_fin >= fecha_inicio`.
- [x] El boton de editar debe ser icono de lapiz con tooltip.
- [x] Mostrar toast de exito/error.

Estado:
- Frontend permite editar nombre e intervalo de fechas.
- Backend permite actualizar nombre, fecha inicio y fecha fin.
- Accion de tabla usa icono de lapiz con tooltip.
- Errores y exitos usan `Toast`.

## Estado: activar/desactivar

- [x] Un periodo inactivo puede activarse.
- [x] Un periodo activo puede desactivarse.
- [x] Debe quedar claro si solo puede existir un periodo activo por tenant.
- [x] Activar un periodo debe explicar si desactiva otros periodos.
- [x] Debe usar modal propio si la accion tiene consecuencia sensible.
- [x] Debe auditarse segun RN-23.

Estado:
- Backend al activar desactiva cualquier otro periodo activo del tenant.
- Frontend usa modal propio para activar, desactivar y eliminar.
- Backend registra auditoria para activar/desactivar periodos.

## Fechas academicas

- [x] Permitir agregar fechas academicas del periodo.
- [x] Permitir quitar fechas academicas si la regla lo permite.
- [x] Fecha academica debe tener tipo/titulo/fecha claros para el usuario.
- [x] Si los documentos piden materia/cohorte, no perder esa asociacion.
- [x] Mostrar toast de exito/error.
- [x] Quitar fecha debe usar modal propio si se considera accion sensible.
- [x] Debe auditarse segun RN-23.

Estado:
- Implementacion actual permite crear, editar y quitar fechas academicas oficiales.
- Las fechas quedan relacionadas al periodo real mediante `periodo_id`.
- Las fechas conservan asociacion a materia y cohorte.
- Frontend usa `Toast` y modal propio.
- Backend registra auditoria para altas, cambios y bajas.

## Programas

- [x] Definir si la seccion de programas de esta pantalla debe usar el modelo objetivo `ProgramaMateria`.
- [x] Segun HU-23, programa requiere materia + carrera + cohorte + titulo + archivo PDF.
- [ ] Debe poder listar, descargar y reemplazar programas existentes.
- [ ] La referencia de archivo debe ser opaca; no path local manipulable.
- [x] Mostrar toast de exito/error.
- [x] Quitar/reemplazar programa debe usar modal propio si se considera accion sensible.
- [x] Debe auditarse segun RN-23.

Estado:
- La seccion de programas en Setup usa `/api/programas` y el modelo oficial.
- La pantalla lista programas y permite alta, edicion de referencia/titulo y baja.
- Sigue pendiente un flujo explicito de descarga/archivo real y una validacion mas estricta sobre la opacidad de la referencia.

## Eliminacion

- [x] No debe existir hard delete.
- [x] Si se expone eliminar, debe ser soft delete.
- [x] Eliminar debe permitirse solo si esta inactivo o si la regla lo permite.
- [x] Debe bloquearse si hay dependencias que obligan a conservar historial.
- [x] Debe usar modal propio, no `window.confirm`.
- [x] Debe mostrar toast especifico.
- [x] Debe auditarse segun RN-23.

Estado:
- Backend actual usa soft delete para periodo.
- Frontend muestra eliminar solo si el periodo esta inactivo.
- Frontend usa modal propio y `Toast`.
- Backend bloquea la eliminacion si el periodo tiene fechas academicas o programas asociados.
- El bloqueo contempla fechas oficiales de `fecha_academica` vinculadas por `periodo_id`.
- Frontend muestra mensaje especifico si el backend bloquea la eliminacion por dependencias.

## UX/UI esperada

- [x] Aplicar `revisiones/criterios-transversales-ux-ui.md`.
- [x] No usar `alert`, `confirm` ni prompts nativos.
- [x] Usar `Toast` compartido para errores y exitos.
- [x] Acciones frecuentes con iconos y tooltips.
- [x] Estado activo/inactivo debe verse claramente.
- [x] Confirmaciones sensibles con modal propio.
- [x] Mensajes especificos y orientados al usuario.
- [x] Mantener consistencia visual con pantallas revisadas.

Estado:
- El modulo ya no usa `Alert` ni `window.confirm`.
- Las acciones secundarias usan iconos con tooltip y las sensibles usan modal propio.
- El modal propio declara `role="dialog"`, `aria-modal`, `aria-labelledby` y `aria-describedby`.
- Periodos, programas y fechas usan `Toast` compartido para errores y exitos.
- La pantalla queda alineada al patron transversal ya usado en Carreras, Cohortes y Materias.

## Reglas de negocio

- [x] Respetar multi-tenancy.
- [x] No hard delete.
- [x] Solo un periodo activo por tenant si esa es la regla confirmada.
- [x] `fecha_fin` no puede ser anterior a `fecha_inicio`.
- [x] Todo cambio significativo debe auditarse segun RN-23.
- [x] Fechas academicas deben representar calendario academico util para Moodle.
- [x] Programas deben respetar HU-23 si se implementan como programas oficiales.

Estado:
- Backend valida tenant mediante repositorios scoped.
- Backend valida rango de fechas.
- Backend activa un solo periodo y desactiva otros.
- Backend audita crear/editar/activar/desactivar/eliminar periodo, y altas/cambios/bajas de fechas y programas.

## Estado actual observado

- [x] Revisar pantalla actual contra este checklist.

## Pendientes recomendados

- [x] Resolver permiso esperado: `estructura:gestionar` vs `periodos:gestionar`.
- [x] Reemplazar `Alert`/`window.confirm` por `Toast` compartido y modales propios.
- [x] Resolver alcance de "Programas" en Setup: asociacion simple al periodo vs HU-23 con PDF/titulo/carrera/cohorte.
- [x] Resolver si fechas academicas deben incluir materia/cohorte en esta pantalla.
- [x] Agregar auditoria RN-23 para acciones significativas del modulo.
