# Checklist de revision - Pantalla Materias

## Fuentes revisadas

- `Funcionalidad.md`
- `knowledge-base/02_descripcion_general.md`
- `knowledge-base/04_modelo_de_datos.md`
- `knowledge-base/06_funcionalidades.md`
- `knowledge-base/10_preguntas_abiertas.md`
- `knowledge-base/11_historias_de_usuario.md`
- `docs/SRS.md`
- `docs/PRD.md`
- `docs/ARQUITECTURA.md`
- `CHANGES.md`
- `revisiones/criterios-transversales-ux-ui.md`

## Alcance esperado

La pantalla de Materias pertenece al modulo de estructura academica. Debe permitir administrar el catalogo unico de materias del tenant, con codigo, nombre, estado y datos requeridos por la vista actual. La materia representa el plan/catalogo; no representa una comision ni un dictado concreto.

ADR-006 cierra el criterio de dominio como `Materia` + `Dictado`: `Materia` es la definicion unica del catalogo y `Dictado` es la instancia por `carrera x cohorte`. Si la pantalla actual usa carrera/cohorte, debe tratarse como filtro/contexto de vista hasta que exista la entidad de dictado/comision correspondiente.

## Permisos esperados

- [x] Solo usuarios con permiso `estructura:gestionar` pueden acceder.
- [x] Deben poder acceder `ADMIN` y `COORDINADOR` si tienen el permiso efectivo.
- [x] El sistema debe resolver acceso por permisos efectivos, no por rol hardcodeado.
- [x] El backend debe validar permisos; la UI no debe ser la unica barrera.

Estado:
- Frontend: ruta `/admin/estructura/materias` y menu usan `PermissionGuard` / `requiredPermission` con `estructura:gestionar`.
- Backend: todos los endpoints `/api/admin/materias` usan `EstructuraGuard = require_permission(ESTRUCTURA_GESTIONAR)`.
- RBAC: `ADMIN` y `COORDINADOR` tienen `estructura:gestionar` en seed/migracion.

## Campos esperados

- [x] `codigo`
  - Obligatorio.
  - Unico por tenant.
  - Ejemplo documentado: `PROG_I`.
- [x] `nombre`
  - Obligatorio.
  - Nombre completo de la materia.
- [x] `estado`
  - Valores esperados: `Activa` / `Inactiva`.
  - Debe mostrarse claramente en listado.
  - Debe poder modificarse con toggle.
- [x] `carga_horaria`
  - Documentada en `Funcionalidad.md` para la pantalla actual.
  - Debe ser numerica.
- [x] `carrera`
  - SRS indica carrera/cohorte segun vista.
  - En el modelo de dominio cerrado por ADR-006, carrera pertenece a la instancia de dictado, no a la definicion pura de materia.
  - Mientras no exista `Dictado`, si la UI lo usa debe tratarse como filtro/contexto y no como comision.
- [x] `cohorte`
  - SRS indica carrera/cohorte segun vista.
  - En el modelo de dominio cerrado por ADR-006, cohorte pertenece a la instancia de dictado, no a la definicion pura de materia.
  - Mientras no exista `Dictado`, si la UI lo usa debe tratarse como filtro/contexto y no como comision.

Estado:
- Backend: `MateriaCreate`, `MateriaUpdate`, `MateriaResponse`, modelo y repositorio contemplan los campos esperados.
- Backend: `codigo` y `nombre` se validan como texto requerido y no pueden quedar vacios o solo con espacios.
- Backend: `codigo` es unico por tenant.
- Backend: `carga_horaria` es numerica.
- Frontend: el formulario permite `codigo`, `nombre`, `carga_horaria` y `estado`.
- Frontend: carrera/cohorte se usan como filtros/contexto de la vista actual.
- Dominio: materia no es comision; la instancia concreta queda pendiente de `Dictado`/comision segun ADR-006.

## Listado

- [x] Mostrar `codigo`.
- [x] Mostrar `nombre`.
- [x] Mostrar `carga_horaria` si la pantalla la gestiona.
- [x] Mostrar estado.
- [x] Mostrar carrera/cohorte solo si la vista actual las usa como contexto.
- [x] Filtrar por carrera y cohorte si la vista actual mantiene ese contexto.
- [x] No mostrar materias eliminadas por soft delete.
- [x] Mostrar acciones disponibles segun estado y reglas de negocio.

Estado:
- Frontend: el listado muestra nombre, codigo, carrera, cohorte, carga horaria y estado.
- Frontend: hay filtros por carrera y cohorte como contexto de la vista actual.
- Frontend: la accion disponible es `Editar`; no se expone `Eliminar`.
- Backend: `GET /api/admin/materias` permite filtrar por `carrera_id` y `cohorte_id`.
- Backend: el listado filtra por tenant actual y `deleted_at IS NULL`.

## Crear materia

- [x] Permitir cargar `codigo`.
- [x] Permitir cargar `nombre`.
- [x] Permitir cargar `carga_horaria`.
- [x] Permitir seleccionar estado inicial `Activa` / `Inactiva`.
- [x] Validar campos obligatorios.
- [x] Validar que el `codigo` no se repita dentro del tenant.
- [x] Mostrar mensaje especifico si el codigo ya existe.
- [x] Si se selecciona carrera/cohorte como contexto, validar que existan y esten activas.
- [x] Si carrera o cohorte estan inactivas, bloquear creacion y mostrar mensaje especifico.
- [x] No usar mensajes genericos cuando se conoce la causa.

Estado:
- Frontend: `Nueva materia` se puede abrir sin aplicar filtros de carrera/cohorte.
- Frontend: el formulario de alta tiene selects propios para `carrera` y `cohorte`; no depende de los filtros del listado.
- Frontend: si hay filtros activos, se usan solo como valores iniciales del formulario.
- Frontend: el formulario envia `codigo`, `nombre`, `carga_horaria`, `estado`, `carrera_id` y `cohorte_id`.
- Frontend: carrera/cohorte son obligatorias para crear en la implementacion actual, pero se capturan dentro del formulario.
- Frontend: hay mensajes especificos para carrera inactiva, cohorte inactiva, codigo duplicado, 404 y campos obligatorios.
- Backend: valida duplicado de `codigo` por tenant.
- Backend: valida carrera existente y activa si se envia `carrera_id`.
- Backend: valida cohorte existente, activa y perteneciente a la carrera si se envia `cohorte_id`.
- Backend: schema valida que `codigo` y `nombre` no queden vacios o solo con espacios.
- Nota de dominio: cuando exista `Dictado`, carrera/cohorte deberian modelarse ahi y no como definicion pura de `Materia`.

## Editar materia

- [x] Permitir editar `codigo`.
- [x] Permitir editar `nombre`.
- [x] Permitir editar `carrera`.
- [x] Permitir editar `cohorte`.
- [x] Permitir editar `carga_horaria`.
- [x] Permitir cambiar `estado` con toggle, no con selector.
- [x] Validar duplicados al editar.
- [x] Mostrar mensaje especifico si el codigo ya existe.
- [x] El boton de editar debe ser un icono de lapiz.
- [x] El icono debe tener tooltip con texto breve.

Estado:
- Frontend: `Editar` carga `codigo`, `nombre`, `carrera`, `cohorte`, `carga_horaria` y `estado` en el formulario.
- Frontend: el guardado de edicion envia `carrera_id` y `cohorte_id` desde los campos del formulario.
- Frontend: el estado se modifica con toggle.
- Frontend: la accion de editar del listado usa icono de lapiz con tooltip `Editar`.
- Frontend: el boton `Actualizar` del formulario en modo edicion muestra icono de lapiz.
- Backend: permite actualizar `codigo`, `nombre`, `carrera_id`, `cohorte_id`, `carga_horaria` y `estado`.
- Backend: valida duplicado de `codigo` dentro del tenant.
- Backend: valida carrera/cohorte existentes, activas y coherentes entre si.
- Backend: schema valida que `codigo` y `nombre` no queden vacios o solo con espacios.

## Estado: activar/desactivar

- [x] Una materia `Activa` puede pasar a `Inactiva`.
- [x] Una materia `Inactiva` puede pasar a `Activa`, si no hay otra regla que lo impida.
- [x] Se puede desactivar una materia sin perder el historico.
- [x] La UI debe dejar claro el estado actual.
- [x] El cambio de estado debe quedar auditado segun RN-23.

Estado:
- Frontend: el formulario usa toggle para cambiar `estado`.
- Frontend: el listado muestra badge `Activa` / `Inactiva`.
- Backend: `PATCH /api/admin/materias/{materia_id}` permite actualizar `estado`.
- Backend: el cambio de estado conserva el registro y no borra historico.
- Backend: el cambio de estado audita `MATERIA_CAMBIAR_ESTADO` con estado anterior y estado nuevo.

## Eliminacion

- [x] Los documentos especificos de Materias piden desactivar; no piden eliminar desde la pantalla.
- [x] No debe existir hard delete.
- [x] No aplica exponer eliminar en UI mientras la decision sea desactivar sin perder historico.
- [x] Si por decision de producto se agrega eliminar, debe ser soft delete.
- [x] Si se agrega eliminar, el backend debe bloquearlo ante dependencias que requieran conservar historial.
- [x] Si se agrega eliminar, debe usar modal propio, toast especifico y auditoria.

Estado:
- Decision aplicada: la pantalla de Materias no ofrece accion de eliminar.
- La operacion correcta para conservar historico es cambiar `estado` a `Inactiva`.
- Frontend: no existe boton `Eliminar`, icono de tacho ni uso de `window.confirm`.
- Backend: no hay hard delete; la baja tecnica existente usa soft delete.
- Pendiente solo si cambia la decision de producto: si se vuelve a exponer eliminar, aplicar bloqueo por dependencias, modal propio, toast especifico y auditoria.

## UX/UI esperada

- [x] Aplicar `revisiones/criterios-transversales-ux-ui.md`.
- [x] Acciones con iconos, no botones largos de texto.
- [x] Editar: icono de lapiz.
- [x] Eliminar: icono de tacho, solo si se decide agregar eliminacion.
- [x] Tooltips breves en hover.
- [x] Iconos con tamano suficiente para ser reconocibles.
- [x] Estado editable con toggle.
- [x] Carga horaria con control numerico.
- [x] Mensajes de error claros y orientados al usuario.
- [x] No mostrar errores genericos cuando se conoce la causa.
- [x] Usar toasts personalizados para errores.
- [x] Usar modal propio para confirmaciones si aplica una accion sensible.
- [x] Mantener consistencia visual con Carreras y Cohortes.

Estado:
- Frontend: la accion de tabla disponible es `Editar`, con icono de lapiz y tooltip.
- Frontend: no se muestra `Eliminar`; por eso no aplica tacho ni modal de confirmacion en Materias.
- Frontend: no usa `alert`, `confirm` ni prompts nativos.
- Frontend: los errores se muestran con toast personalizado, cierre manual y autocierre a los 5 segundos.
- Frontend: altas y ediciones muestran toast de exito con el componente compartido.
- Frontend: los errores conocidos tienen mensajes especificos: carrera inactiva, cohorte inactiva, codigo duplicado, 404 y campos obligatorios.
- Frontend: estado con toggle y carga horaria con input numerico.
- Transversal: no se implementan acciones que no esten pedidas por documentos o decision explicita.
- Transversal: Materias reutiliza el patron comun de `Toast` definido para las pantallas revisadas.

## Reglas de negocio

- [x] Materia es catalogo unico por tenant.
- [x] La materia no es una comision.
- [x] El codigo de materia es unico por tenant.
- [x] Las entidades inactivas se conservan para historico.
- [x] Todo cambio debe respetar multi-tenancy.
- [x] No debe haber borrado fisico.
- [x] Toda accion significativa debe auditarse segun RN-23.
- [x] Si se usa carrera/cohorte, no debe contradecir ADR-006: la instancia concreta debe resolverse con `Dictado`/comision cuando esa entidad exista.

Estado:
- Backend: repositories filtran por `tenant_id` y `deleted_at IS NULL`.
- Backend: `codigo` es unico por tenant; `nombre` puede repetirse.
- Backend: no hay hard delete; la baja tecnica usa soft delete.
- Backend: crear, editar, cambiar estado y baja tecnica de Materia quedan auditados con `MATERIA_CREAR`, `MATERIA_EDITAR`, `MATERIA_CAMBIAR_ESTADO` y `MATERIA_ELIMINAR`.
- Frontend: no expone eliminacion; la accion funcional para conservar historico es desactivar.
- Dominio: se mantiene la aclaracion de que carrera/cohorte son contexto actual hasta que exista `Dictado`/comision.

## Estado actual observado

- [x] Revisar pantalla actual contra este checklist.

Estado:
- La pantalla de Materias queda revisada contra permisos, campos, listado, crear, editar, estado, eliminacion, UX/UI y reglas de negocio.
- No quedan pendientes funcionales documentados para esta pantalla dentro del alcance actual.

## Pendientes recomendados

- [ ] Pendiente de dominio futuro: cuando se implemente `Dictado`/comision, mover la logica de instancia concreta fuera de la definicion pura de `Materia`.
