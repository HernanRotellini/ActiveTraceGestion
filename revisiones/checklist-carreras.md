# Checklist de revision - Pantalla Carreras

## Fuentes revisadas

- `Funcionalidad.md`
- `knowledge-base/04_modelo_de_datos.md`
- `knowledge-base/06_funcionalidades.md`
- `knowledge-base/11_historias_de_usuario.md`
- `docs/SRS.md`
- `docs/PRD.md`
- `CHANGES.md`

## Alcance esperado

La pantalla de Carreras pertenece al modulo de estructura academica. Debe permitir administrar el catalogo de carreras de un tenant, manteniendo trazabilidad, estado operativo y reglas de integridad con cohortes/asignaciones asociadas.

## Permisos esperados

- [x] Solo usuarios con rol `ADMIN` o `COORDINADOR` pueden acceder.
  - HU-21 indica `COORDINADOR` o `ADMIN`.
  - El sistema trabaja por permisos efectivos, no por rol hardcodeado.
  - Se agrego `estructura:gestionar` a `COORDINADOR` para respetar HU-21.
- [x] La accion debe estar protegida por permiso `estructura:gestionar`.
  - `docs/SRS.md` define `estructura:gestionar` para `/admin/estructura/carreras`.
  - La ruta frontend usa `PermissionGuard requiredPermissions={['estructura:gestionar']}`.
  - El router backend usa `require_permission(ESTRUCTURA_GESTIONAR)`.
- [x] El backend debe validar permisos; la UI no debe ser la unica barrera.
  - El backend valida el JWT y los permisos efectivos server-side.
  - Sin permiso efectivo, responde `403`.

## Revision de permisos

- [x] Frontend: la ruta `/admin/estructura/carreras` esta protegida por `PermissionGuard`.
- [x] Frontend: el menu oculta Carreras si falta `estructura:gestionar`.
- [x] Backend: todos los endpoints de carreras usan el guard `estructura:gestionar`.
- [x] Backend: la identidad y tenant se resuelven desde JWT verificado.
- [x] Seed RBAC: `ADMIN` tiene `estructura:gestionar`.
- [x] Seed RBAC: `COORDINADOR` tiene `estructura:gestionar`.
- [x] Decision definida: Carreras queda disponible para `ADMIN` y `COORDINADOR`, respetando HU-21.

## Campos esperados

- [x] `codigo`
  - Obligatorio.
  - Unico por tenant.
  - Editable si no rompe reglas de negocio.
- [x] `nombre`
  - Obligatorio.
  - Segun HU-21, no deberia repetirse.
  - Se valida unicidad por tenant en backend.
  - Se agrega indice unico parcial para carreras no eliminadas.
- [x] `descripcion`
  - Campo complementario mencionado en `Funcionalidad.md`.
  - No aparece como campo central en todos los documentos, pero puede mantenerse.
- [x] `estado`
  - Valores esperados: `Activa` / `Inactiva`.
  - Debe mostrarse claramente en el listado.
  - Debe poder modificarse desde la edicion o mediante accion directa.
  - Backend acepta solo `activa` / `inactiva`.

## Listado

- [x] Mostrar `codigo`.
- [x] Mostrar `nombre`.
- [x] Mostrar `descripcion` si existe.
- [x] Mostrar `estado`.
- [x] Mostrar acciones disponibles segun estado y reglas de negocio.
- [x] Incluir filtros por codigo, nombre y/o estado, segun `docs/SRS.md`.
  - Filtros agregados: nombre, codigo y estado.
  - Backend valida `estado` como `activa` / `inactiva`.
- [x] No mostrar carreras eliminadas por soft delete.
  - El repository base lista solo registros con `deleted_at IS NULL`.

## Crear carrera

- [x] Permitir crear carrera con `codigo`.
- [x] Permitir crear carrera con `nombre`.
- [x] Permitir cargar `descripcion` si se mantiene el campo.
- [x] Permitir seleccionar estado inicial.
  - Los documentos no obligan a crear siempre como `Activa`.
  - HU-21 define estados posibles `Activa` / `Inactiva`.
  - La pantalla permite elegir `Activa` / `Inactiva` con toggle al crear.
- [x] Validar codigo obligatorio.
- [x] Validar nombre obligatorio.
- [x] Validar codigo unico por tenant.
- [x] Validar nombre unico si se adopta el criterio de HU-21.
- [x] Mostrar mensajes especificos ante errores de unicidad.
- [x] No usar mensajes genericos cuando el problema sea identificable.

## Editar carrera

- [x] Permitir editar `codigo`.
- [x] Permitir editar `nombre`.
- [x] Permitir editar `descripcion`.
- [x] Permitir cambiar `estado` con un toggle, no con selector.
- [x] Validar duplicados al editar.
  - Backend valida `codigo` duplicado.
  - Backend valida `nombre` duplicado.
- [x] Mostrar mensaje especifico si el codigo ya existe.
- [x] Mostrar mensaje especifico si el nombre ya existe, si se adopta unicidad por nombre.
- [x] El boton de editar debe ser un icono de lapiz.
- [x] El icono debe tener tooltip con texto breve.

## Estado: activar/desactivar

- [x] Una carrera `Activa` puede pasar a `Inactiva`.
- [x] Una carrera `Inactiva` puede pasar a `Activa`, si no hay otra regla que lo impida.
- [x] Una carrera `Inactiva` no debe permitir crear nuevas cohortes abiertas.
  - Backend bloquea `create_cohorte` si `carrera.estado != "activa"`.
- [x] El cambio de estado debe quedar auditado.
  - Se registra `CARRERA_CAMBIAR_ESTADO` solo si el estado cambia.
  - Detalle auditado: `carrera_id`, `codigo`, `nombre`, `estado_anterior`, `estado_nuevo`.
- [x] La UI debe dejar claro el estado actual.
  - El listado muestra badge `Activa` / `Inactiva`.
  - El formulario muestra toggle con el estado actual.

## Eliminacion

- [x] No debe existir hard delete.
- [x] Si se permite eliminar, debe ser soft delete.
- [x] Segun HU-21/SRS, una carrera con cohortes o asignaciones asociadas no deberia eliminarse; solo desactivarse.
- [x] El backend debe bloquear la eliminacion si existen cohortes asociadas.
- [x] El backend debe bloquear la eliminacion si existen asignaciones asociadas.
- [x] La UI debe ocultar o deshabilitar la accion de eliminar cuando no corresponde.
  - La UI oculta eliminar para carreras activas.
  - Las dependencias se validan en backend y se informan con mensaje especifico.
- [x] Si se mantiene eliminar, el boton debe mostrarse solo para carreras inactivas y sin dependencias.
  - Sin dependencias se garantiza en backend; la UI no tiene conteos de dependencias en el listado.
- [x] El boton de eliminar debe ser un icono de tacho.
- [x] El icono debe tener tooltip con texto breve.
- [x] Debe pedir confirmacion antes de eliminar.
- [x] Debe mostrar un mensaje especifico si no se puede eliminar por dependencias.

## UX/UI esperada

- [x] Acciones con iconos, no botones largos de texto.
- [x] Editar: icono de lapiz.
- [x] Eliminar: icono de tacho, solo si aplica.
- [x] Tooltips breves en hover.
- [x] Iconos con tamano suficiente para ser reconocibles.
- [x] Estado editable con toggle.
- [x] Mensajes de error claros y orientados al usuario.
  - Errores se muestran como toast personalizado.
  - Los toasts se cierran automaticamente a los 5 segundos.
- [x] No mostrar errores genericos cuando se conoce la causa.
- [x] Mantener consistencia visual con Cohortes y Materias.
  - Carreras, Cohortes y Materias usan el componente compartido `Toast`.
  - Las pantallas revisadas no usan `alert`, `confirm` ni prompts nativos.
  - Ver criterio transversal: `revisiones/criterios-transversales-ux-ui.md`.

## Reglas de negocio

- [x] `codigo` unico por tenant.
  - Se valida en service.
  - Se garantiza por constraint/indice en base.
  - Puede repetirse en tenants distintos.
- [x] Evaluar y definir si `nombre` tambien debe ser unico por tenant.
  - Decision: `nombre` tambien es unico por tenant, respetando HU-21.
  - Puede repetirse en tenants distintos.
- [x] Carrera inactiva no permite crear cohortes abiertas.
  - Backend bloquea `create_cohorte` cuando la carrera no esta `activa`.
- [x] Carrera con cohortes/asignaciones no se elimina; se desactiva.
  - Backend bloquea eliminacion con cohortes asociadas.
  - Backend bloquea eliminacion con asignaciones asociadas.
- [x] Todo cambio debe respetar multi-tenancy.
  - Repositories usan `tenant_id` por defecto.
  - Listado no muestra carreras de otros tenants.
  - Eliminacion cross-tenant devuelve `404` y no afecta el registro externo.
- [x] Toda baja debe ser soft delete.
  - Se usa `deleted_at`; no hay hard delete.
- [x] Toda accion relevante debe quedar auditada.
  - Alta audita `CARRERA_CREAR`.
  - Edicion general audita `CARRERA_EDITAR`.
  - Cambio de estado audita `CARRERA_CAMBIAR_ESTADO`.
  - Soft delete audita `CARRERA_ELIMINAR`.

## Estado actual observado

- [x] La pantalla lista carreras.
- [x] Permite crear carreras.
- [x] Permite editar carreras.
- [x] Muestra estado `Activa` / `Inactiva`.
- [x] Permite cambiar estado con toggle.
- [x] Permite crear carreras como `Activa` o `Inactiva`.
- [x] Filtra por codigo, nombre y estado.
- [x] Usa icono de lapiz para editar.
- [x] Usa icono de tacho para eliminar.
- [x] Muestra tooltips en acciones.
- [x] Eliminar se muestra solo si la carrera esta inactiva.
- [x] La eliminacion implementada es soft delete.
- [x] Backend bloquea eliminacion con cohortes/asignaciones.
- [x] Backend bloquea eliminacion de carreras activas.
- [x] Backend valida unicidad de codigo.
- [x] Backend valida unicidad de nombre.
- [x] Errores se muestran con toast personalizado.
- [x] Altas, ediciones y eliminaciones muestran toast de exito con el componente compartido.
- [x] Confirmacion de eliminacion usa modal propio.
- [x] Acciones relevantes se auditan: crear, editar, cambiar estado y soft delete.
- [x] Tests backend de Carreras cubren reglas principales.
- [x] Tests frontend renderizan la pantalla dentro del suite `EstructuraAcademica`.

## Pendientes recomendados

- [x] No quedan pendientes documentales especificos para Carreras.
- [ ] Pendiente transversal fuera del alcance de Carreras: aplicar `revisiones/criterios-transversales-ux-ui.md` al revisar el resto de pantallas.
