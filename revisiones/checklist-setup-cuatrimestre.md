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
- [ ] Registrar fechas academicas asociadas al periodo, revisando si tambien deben asociarse a materia/cohorte.
- [ ] Gestionar programas oficiales solo si se respeta HU-23: materia + carrera + cohorte + titulo + archivo PDF/referencia opaca.

Fuera del alcance directo de esta pantalla, salvo decision explicita de producto:
- [x] Clonado real de equipo docente: pertenece a `equipos:asignar`.
- [x] Alta masiva o ajuste de asignaciones docentes: pertenece a equipos/asignaciones.
- [x] Publicacion de avisos: pertenece a avisos.
- [x] Importacion de padron inicial: pertenece a padron/importacion.

Estado:
- La pantalla actual cubre periodos, fechas simples y asociacion simple de programas/materias.
- Hay que revisar si las secciones de fechas y programas actuales cumplen los requisitos documentales o si deben recortarse/reformularse.

## Permisos esperados

- [x] Definir permiso final de la pantalla segun documentos.
- [x] Deben poder acceder `ADMIN` y `COORDINADOR` si tienen el permiso efectivo.
- [x] El sistema debe resolver acceso por permisos efectivos, no por rol hardcodeado.
- [x] El backend debe validar permisos; la UI no debe ser la unica barrera.

Estado:
- Permiso esperado documental: `estructura:gestionar`, declarado por `docs/SRS.md` para `/coordinacion/setup-cuatrimestre`.
- Implementacion actual: ruta frontend, menu, backend y seed usan `periodos:gestionar`, por lo tanto no respeta literalmente el SRS.
- Frontend actual: `PermissionGuard` y menu validan `periodos:gestionar`.
- Backend actual: todos los endpoints `/api/periodos-academicos` usan `require_permission(PERIODOS_GESTIONAR)`.
- `ADMIN` y `COORDINADOR` tienen `periodos:gestionar` en `backend/scripts/seed_rbac.py`.
- Decision recomendada para respetar documentos: cambiar pantalla, menu y backend a `estructura:gestionar`.
- Pendiente de implementacion: aplicar cambio RBAC en codigo si se confirma esta decision.

## Campos esperados

- [ ] Periodo academico:
  - `nombre`.
  - `fecha_inicio`.
  - `fecha_fin`.
  - `activo`.
- [ ] Fecha academica:
  - Tipo o clave de fecha.
  - Titulo/etiqueta.
  - Fecha.
  - Asociacion al periodo.
  - Segun SRS/modelo objetivo: asociacion a materia/cohorte cuando aplique.
- [ ] Programa:
  - Materia.
  - Carrera.
  - Cohorte.
  - Titulo.
  - Archivo PDF o referencia de archivo opaca.

Estado:
- Frontend/backend actuales de periodo usan `nombre`, `fecha_inicio`, `fecha_fin`, `activo`.
- Fechas actuales usan `key`, `label`, `fecha` dentro de un periodo; no capturan materia/cohorte.
- Programas actuales dentro de periodo usan `materia_id`, `carrera` texto y `anio`; no capturan cohorte, titulo ni archivo PDF.
- Existe router separado `/api/programas` que modela `materia_id`, `carrera_id`, `cohorte_id`, `titulo` y `referencia_archivo`, mas cercano a HU-23.

## Listado

- [ ] Listar periodos academicos.
- [ ] Mostrar rango de vigencia inicio/fin.
- [ ] Mostrar estado activo/inactivo.
- [ ] Mostrar fechas academicas del periodo.
- [ ] Mostrar programas asociados del periodo si la pantalla mantiene esa seccion.
- [ ] No mostrar periodos eliminados por soft delete.
- [ ] Mostrar acciones disponibles segun estado y reglas de negocio.

Estado:
- Frontend lista periodos con nombre, rango, estado, fechas y programas.
- Backend lista por tenant y no deberia mostrar soft deleted.
- Acciones actuales: activar/desactivar, editar, eliminar si inactivo, agregar/quitar fechas y programas.

## Crear periodo

- [ ] Permitir cargar `nombre`.
- [ ] Permitir seleccionar `fecha_inicio`.
- [ ] Permitir seleccionar `fecha_fin`.
- [ ] Validar campos obligatorios.
- [ ] Validar que `fecha_fin >= fecha_inicio`.
- [ ] Mostrar mensajes especificos, no genericos.
- [ ] Confirmar si el periodo se crea activo o inactivo por defecto.

Estado:
- Frontend valida obligatorios y rango de fechas.
- Backend valida `fecha_fin >= fecha_inicio`.
- El periodo se crea inactivo por defecto segun modelo actual.
- Pendiente UX: errores deben mostrarse con `Toast`, no `Alert`.

## Editar periodo

- [ ] Permitir editar `nombre`.
- [ ] Permitir editar `fecha_inicio`.
- [ ] Permitir editar `fecha_fin`.
- [ ] Validar que `fecha_fin >= fecha_inicio`.
- [ ] El boton de editar debe ser icono de lapiz con tooltip.
- [ ] Mostrar toast de exito/error.

Estado:
- Frontend permite editar nombre e intervalo de fechas.
- Backend permite actualizar nombre, fecha inicio y fecha fin.
- Accion de tabla usa icono de lapiz con tooltip.
- Pendiente UX: errores y exitos deben usar `Toast`.

## Estado: activar/desactivar

- [ ] Un periodo inactivo puede activarse.
- [ ] Un periodo activo puede desactivarse.
- [ ] Debe quedar claro si solo puede existir un periodo activo por tenant.
- [ ] Activar un periodo debe explicar si desactiva otros periodos.
- [ ] Debe usar modal propio si la accion tiene consecuencia sensible.
- [ ] Debe auditarse segun RN-23.

Estado:
- Backend actual al activar desactiva cualquier otro periodo activo del tenant.
- Frontend usa `window.confirm`, debe reemplazarse por modal propio.
- Backend actual no registra auditoria visible para activar/desactivar periodos.

## Fechas academicas

- [ ] Permitir agregar fechas academicas del periodo.
- [ ] Permitir quitar fechas academicas si la regla lo permite.
- [ ] Fecha academica debe tener tipo/titulo/fecha claros para el usuario.
- [ ] Si los documentos piden materia/cohorte, no perder esa asociacion.
- [ ] Mostrar toast de exito/error.
- [ ] Quitar fecha debe usar modal propio si se considera accion sensible.
- [ ] Debe auditarse segun RN-23.

Estado:
- Implementacion actual permite agregar/quitar `key`, `label`, `fecha`.
- Implementacion actual no asocia fecha a materia/cohorte, aunque SRS y modelo objetivo lo mencionan.
- Frontend usa `Alert` para errores y `window.confirm` para quitar.
- Backend actual no registra auditoria visible para agregar/quitar fechas.

## Programas

- [ ] Definir si la seccion de programas de esta pantalla debe usar el modelo objetivo `ProgramaMateria`.
- [ ] Segun HU-23, programa requiere materia + carrera + cohorte + titulo + archivo PDF.
- [ ] Debe poder listar, descargar y reemplazar programas existentes.
- [ ] La referencia de archivo debe ser opaca; no path local manipulable.
- [ ] Mostrar toast de exito/error.
- [ ] Quitar/reemplazar programa debe usar modal propio si se considera accion sensible.
- [ ] Debe auditarse segun RN-23.

Estado:
- La seccion actual de programas en Setup no sube PDF ni titulo; solo asocia materia, carrera texto y año al periodo.
- Existe `/api/programas`, que representa mejor HU-23, pero la pantalla actual no lo usa.
- Pendiente de decision: mantener "Programas" dentro de Setup como asignacion simple al periodo, o reemplazarla por flujo real de ProgramaMateria.

## Eliminacion

- [ ] No debe existir hard delete.
- [ ] Si se expone eliminar, debe ser soft delete.
- [ ] Eliminar debe permitirse solo si esta inactivo o si la regla lo permite.
- [ ] Debe bloquearse si hay dependencias que obligan a conservar historial.
- [ ] Debe usar modal propio, no `window.confirm`.
- [ ] Debe mostrar toast especifico.
- [ ] Debe auditarse segun RN-23.

Estado:
- Backend actual usa soft delete para periodo.
- Frontend muestra eliminar solo si el periodo esta inactivo.
- Frontend usa `window.confirm`, debe reemplazarse por modal propio.
- No se observo bloqueo por dependencias ni auditoria visible de baja.

## UX/UI esperada

- [ ] Aplicar `revisiones/criterios-transversales-ux-ui.md`.
- [ ] No usar `alert`, `confirm` ni prompts nativos.
- [ ] Usar `Toast` compartido para errores y exitos.
- [ ] Acciones frecuentes con iconos y tooltips.
- [ ] Estado activo/inactivo debe verse claramente.
- [ ] Confirmaciones sensibles con modal propio.
- [ ] Mensajes especificos y orientados al usuario.
- [ ] Mantener consistencia visual con pantallas revisadas.

Estado:
- Frontend actual usa `Alert` y `window.confirm`.
- Algunas acciones usan iconos con tooltip.
- Activar/desactivar son botones de texto; revisar si conviene mantener por claridad o mover a patron de accion consistente.

## Reglas de negocio

- [ ] Respetar multi-tenancy.
- [ ] No hard delete.
- [ ] Solo un periodo activo por tenant si esa es la regla confirmada.
- [ ] `fecha_fin` no puede ser anterior a `fecha_inicio`.
- [ ] Todo cambio significativo debe auditarse segun RN-23.
- [ ] Fechas academicas deben representar calendario academico util para Moodle.
- [ ] Programas deben respetar HU-23 si se implementan como programas oficiales.

Estado:
- Backend valida tenant mediante repositorios scoped.
- Backend valida rango de fechas.
- Backend activa un solo periodo y desactiva otros.
- Pendiente: auditoria de crear/editar/activar/desactivar/eliminar periodo, agregar/quitar fechas y agregar/quitar programas.

## Estado actual observado

- [ ] Revisar pantalla actual contra este checklist.

## Pendientes recomendados

- [ ] Resolver permiso esperado: `estructura:gestionar` vs `periodos:gestionar`.
- [ ] Reemplazar `Alert`/`window.confirm` por `Toast` compartido y modales propios.
- [ ] Resolver alcance de "Programas" en Setup: asociacion simple al periodo vs HU-23 con PDF/titulo/carrera/cohorte.
- [ ] Resolver si fechas academicas deben incluir materia/cohorte en esta pantalla.
- [ ] Agregar auditoria RN-23 para acciones significativas del modulo.
