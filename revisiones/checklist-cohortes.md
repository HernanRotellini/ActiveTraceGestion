# Checklist de revision - Pantalla Cohortes

## Fuentes revisadas

- `Funcionalidad.md`
- `knowledge-base/04_modelo_de_datos.md`
- `knowledge-base/06_funcionalidades.md`
- `knowledge-base/11_historias_de_usuario.md`
- `knowledge-base/05_reglas_de_negocio.md`
- `docs/SRS.md`
- `docs/PRD.md`
- `CHANGES.md`
- `revisiones/criterios-transversales-ux-ui.md`

## Alcance esperado

La pantalla de Cohortes pertenece al modulo de estructura academica. Debe permitir administrar cohortes asociadas a una carrera, con nombre, año, vigencia y estado, preservando historial y evitando operaciones inconsistentes sobre carreras inactivas.

## Permisos esperados

- [x] Solo usuarios con permiso `estructura:gestionar` pueden acceder.
- [x] HU-22 indica `COORDINADOR` o `ADMIN`; F5.2 menciona `ADMIN`.
- [x] Criterio esperado: deben poder acceder `ADMIN` y `COORDINADOR`.
- [x] Criterio tecnico: respetar `estructura:gestionar` como permiso fuente y no hardcodear rol.
- [x] El sistema debe resolver acceso por permisos efectivos, no por rol hardcodeado.
- [x] El backend debe validar permisos; la UI no debe ser la unica barrera.

Estado:
- Frontend: ruta `/admin/estructura/cohortes` y menu usan `PermissionGuard` / `requiredPermission` con `estructura:gestionar`.
- Backend: todos los endpoints `/api/admin/cohortes` usan `EstructuraGuard = require_permission(ESTRUCTURA_GESTIONAR)`.
- RBAC: `ADMIN` y `COORDINADOR` tienen `estructura:gestionar` en seed/migracion.

## Campos esperados

- [x] `carrera`
  - Obligatoria.
  - La cohorte pertenece a una carrera segun el modelo actual y `docs/SRS.md`.
  - PA-07 indica que la cardinalidad debe validarse con negocio, pero el modelo actual asocia Cohorte a Carrera.
- [x] `nombre`
  - Obligatorio.
  - Ejemplos documentados: `MAR-2025`, `AGO-2025`, `MAR-2026`.
  - Unico por tenant + carrera.
- [x] `anio`
  - Obligatorio.
  - Debe representar el año de inicio.
- [x] `vig_desde`
  - Obligatorio.
  - Fecha de inicio.
- [x] `vig_hasta`
  - Opcional.
  - Fecha de fin; si no existe, la cohorte queda abierta.
- [x] `estado`
  - Valores esperados: `Activa` / `Inactiva`.
  - Debe mostrarse claramente en listado.
  - Debe poder modificarse con toggle.

Estado:
- Backend: `CohorteCreate`, `CohorteUpdate`, `CohorteResponse`, modelo y repositorio contemplan todos los campos esperados.
- Backend: `nombre` se valida como texto requerido y no puede quedar vacio o solo con espacios.
- Base de datos: existe unique constraint `tenant_id + carrera_id + nombre`.
- Frontend: el formulario permite carrera, nombre, año, vigencia desde/hasta y estado.

## Listado

- [x] Mostrar carrera seleccionada o filtro de carrera.
- [x] Mostrar `nombre`.
- [x] Mostrar `anio`.
- [x] Mostrar vigencia desde / hasta.
- [x] Mostrar estado.
- [x] Mostrar acciones disponibles segun estado y reglas de negocio.
- [x] Filtrar por carrera.
- [x] Los documentos no exigen filtros adicionales por nombre, año o estado para Cohortes.
- [x] No mostrar cohortes eliminadas por soft delete.

Estado:
- Frontend: el listado muestra filtro de carrera, nombre, año, vigencia desde/hasta y estado.
- Backend: `GET /api/admin/cohortes` permite filtrar por `carrera_id`.
- Backend: repositorio lista solo registros del tenant actual y con `deleted_at IS NULL`.
- Frontend: la accion de eliminar no se expone; la baja funcional se hace cambiando estado a `Inactiva`.

## Crear cohorte

- [x] Permitir seleccionar carrera.
- [x] No permitir crear cohortes abiertas sobre carrera inactiva.
- [x] Mostrar mensaje especifico si la carrera esta inactiva.
- [x] Permitir cargar `nombre`.
- [x] Permitir cargar `anio`.
- [x] Permitir seleccionar `vig_desde` con selector de fecha.
- [x] Permitir seleccionar `vig_hasta` con selector de fecha.
- [x] Permitir dejar `vig_hasta` vacia.
- [x] Permitir seleccionar estado inicial `Activa` / `Inactiva`.
- [x] Validar campos obligatorios.
- [x] Validar que el nombre no se repita dentro de la misma carrera.
- [x] Mostrar mensaje especifico si el nombre ya existe.
- [x] No usar mensajes genericos cuando se conoce la causa.

Estado:
- Frontend: `Nueva cohorte` se habilita al seleccionar carrera y el formulario envia `carrera_id`, `nombre`, `anio`, `vig_desde`, `vig_hasta` y `estado`.
- Frontend: `vig_hasta` puede quedar vacia y no se envia como requerida.
- Frontend: hay mensajes especificos para carrera inactiva, duplicado y campos obligatorios.
- Backend: valida carrera existente, bloquea carrera inactiva y valida duplicado por carrera.
- Backend: schema valida que `nombre` no quede vacio o solo con espacios.
- UX: los mensajes de error se muestran con toast personalizado.

## Editar cohorte

- [x] Permitir editar `nombre`.
- [x] Permitir editar `anio`.
- [x] Permitir editar `vig_desde`.
- [x] Permitir editar `vig_hasta`.
- [x] Permitir limpiar `vig_hasta`.
- [x] Permitir cambiar `estado` con toggle, no con selector.
- [x] Validar duplicados al editar.
- [x] Mostrar mensaje especifico si el nombre ya existe en la misma carrera.
- [x] El boton de editar debe ser un icono de lapiz.
- [x] El icono debe tener tooltip con texto breve.

Estado:
- Frontend: `Editar` carga `nombre`, `anio`, `vig_desde`, `vig_hasta` y `estado` en el formulario.
- Frontend: el guardado de edicion envia `vig_hasta: null` cuando se limpia.
- Frontend: el estado se modifica con toggle.
- Frontend: la accion de editar del listado usa icono de lapiz con tooltip `Editar`.
- Frontend: el boton `Actualizar` del formulario en modo edicion muestra icono de lapiz.
- Backend: valida duplicado de `nombre` dentro de la misma carrera y permite actualizar vigencia/estado.
- UX: los mensajes de error se muestran con toast personalizado.

## Estado: activar/desactivar

- [x] Una cohorte `Activa` puede pasar a `Inactiva`.
- [x] Una cohorte `Inactiva` puede pasar a `Activa`, si no hay otra regla que lo impida.
- [x] Se puede desactivar una cohorte sin perder el historico.
- [x] La UI debe dejar claro el estado actual.
- [x] El cambio de estado debe quedar auditado si se considera accion significativa segun RN-23.

Estado:
- Frontend: el formulario usa toggle para cambiar `estado`.
- Frontend: el listado muestra badge `Activa` / `Inactiva`.
- Backend: `PATCH /api/admin/cohortes/{cohorte_id}` permite actualizar `estado`.
- Backend: el cambio de estado conserva el registro y no borra historico.
- Backend: el cambio de estado audita `COHORTE_CAMBIAR_ESTADO` con estado anterior y estado nuevo.
- Transversal: se agrego criterio global de auditoria en `revisiones/criterios-transversales-ux-ui.md`.

## Eliminacion

- [x] Los documentos especificos de Cohortes no piden eliminar; piden desactivar sin perder historico.
- [x] No debe existir hard delete.
- [x] No aplica exponer eliminar en UI mientras la decision sea desactivar sin perder historico.
- [x] No aplica icono de tacho en Cohortes mientras no se exponga eliminar.
- [x] No aplica modal de confirmacion de eliminar mientras no se exponga eliminar.
- [x] No aplica toast de error de eliminar mientras no se exponga eliminar.

Estado:
- Decision aplicada: la pantalla de Cohortes no ofrece accion de eliminar.
- La operacion correcta para conservar historico es cambiar `estado` a `Inactiva`.
- Frontend: se removio el boton `Eliminar`, el icono de tacho y el uso de `window.confirm`.
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
- [x] Fechas con inputs/selector de calendario.
- [x] Año con control adecuado para año.
- [x] Mensajes de error claros y orientados al usuario.
- [x] No mostrar errores genericos cuando se conoce la causa.
- [x] Usar toasts personalizados para errores.
- [x] Usar modal propio para confirmaciones.
- [x] Mantener consistencia visual con Carreras y Materias.

Estado:
- Frontend: la accion de tabla disponible es `Editar`, con icono de lapiz y tooltip.
- Frontend: no se muestra `Eliminar`; por eso no aplica tacho ni modal de confirmacion en Cohortes.
- Frontend: no usa `alert`, `confirm` ni prompts nativos.
- Frontend: los errores se muestran con toast personalizado, cierre manual y autocierre a los 5 segundos.
- Frontend: altas y ediciones muestran toast de exito con el componente compartido.
- Frontend: los errores conocidos tienen mensajes especificos: carrera inactiva, duplicado, 404 y campos obligatorios.
- Frontend: estado con toggle, fechas con `input type="date"` y año con selector.
- Transversal: Cohortes reutiliza el patron comun de `Toast` definido para las pantallas revisadas.
- Nota: Materias se revisa despues para llevarla al mismo patron.

## Reglas de negocio

- [x] Cohorte pertenece a una carrera segun modelo actual.
- [x] Nombre unico por tenant + carrera.
- [x] Carrera inactiva no admite nuevas cohortes abiertas.
- [x] Fecha de inicio obligatoria.
- [x] Fecha de fin opcional.
- [x] Desactivar no debe borrar historial.
- [x] Todo cambio debe respetar multi-tenancy.
- [x] No debe haber borrado fisico; las entidades inactivas se conservan para historico.
- [x] Toda accion significativa debe auditarse segun RN-23.

Estado:
- Backend: `carrera_id` es obligatorio y se valida contra carrera existente del mismo tenant.
- Backend: `nombre` es unico por `tenant_id + carrera_id` y se valida en create/update.
- Backend: una carrera inactiva bloquea la creacion de cohortes.
- Backend: `vig_desde` es obligatorio y `vig_hasta` opcional.
- Backend: repositories filtran por `tenant_id` y `deleted_at IS NULL`.
- Backend: la baja tecnica disponible es soft delete; la UI no la expone para Cohortes.
- Backend: se auditan `COHORTE_CREAR`, `COHORTE_EDITAR`, `COHORTE_CAMBIAR_ESTADO` y `COHORTE_ELIMINAR`.

## Estado actual observado

- [x] Revisar pantalla actual contra este checklist.

Estado:
- Pantalla Cohortes revisada completa contra fuentes, checklist y criterios transversales.
- No quedan pendientes funcionales documentados para Cohortes.

## Pendientes recomendados

- [x] Completar despues de revisar la implementacion actual de Cohortes.

Estado:
- No hay pendientes recomendados especificos de Cohortes.
- Toasts de exito aplicados en Cohortes; las proximas pantallas deben reutilizar el componente compartido.
