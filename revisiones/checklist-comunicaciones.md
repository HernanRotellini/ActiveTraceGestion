# Checklist - Pantalla Comunicaciones

## Fuentes revisadas

- `docs/PRD.md`: RF-17 preview obligatorio del mail; RF-18 cola con estados Pend/Send/OK/Fail/Canc; RF-19 aprobacion humana opcional por tenant; RF-20 plantillas con variables `{{alumno.nombre}}`. Asociadas a HU-10/HU-11/HU-12.
- `docs/SRS.md`: `/docente/comunicaciones` requiere `comunicacion:enviar`; datos = lotes, estados, preview, destinatarios; acciones = previsualizar, encolar, seguir estados. Flujo "Crear, aprobar y enviar comunicaciones" (preview → encolar Pendiente por alumno agrupado por `lote_id` → aprobar/cancelar lote → tracking). Reglas: envios masivos pueden requerir aprobacion por tenant; destinatarios cifrados; envio/aprobacion/cancelacion auditan. Permisos `comunicacion:enviar` y `comunicacion:aprobar`. Worker async despacha.
- `knowledge-base/05_reglas_de_negocio.md`: RN-15 ciclo de vida (Pendiente→Enviando→Enviado/Fallido/Cancelado); RN-16 vista previa obligatoria; RN-17 aprobacion administrativa de envios masivos via `comunicacion:aprobar`.
- `knowledge-base/06_funcionalidades.md`: F3.1 vista previa; F3.2 envio masivo con cola y tracking; F3.3 aprobacion de envios masivos.
- `knowledge-base/07_flujos_principales.md`: FL-04 (Parte A generacion PROFESOR; Parte B aprobacion COORDINADOR/`comunicacion:aprobar`, aprobar/cancelar lote o por destinatario; Parte C seguimiento con panel de estado por materia y destinatario).
- `knowledge-base/11_historias_de_usuario.md`: HU-10 previsualizar; HU-11 enviar recordatorios masivos a atrasados con conteo de estados; HU-12 aprobar/cancelar antes del despacho.
- `knowledge-base/03_actores_y_roles.md`: PROFESOR comunica sobre sus comisiones; COORDINADOR/ADMIN aprueban comunicaciones masivas.
- Backend real: `backend/app/api/v1/routers/comunicaciones.py` (preview, enviar, lotes, lotes/{id}, lotes/{id}/aprobar, lotes/{id}/cancelar, {id}/cancelar), `comunicacion_service.py`, `comunicacion_repository.py`, modelo `comunicacion.py` (estados Pendiente/Enviando/Enviado/Error/Cancelado), worker `comunicaciones_worker.py`.

## Alcance esperado

- [x] Componer una comunicacion (materia, asunto, cuerpo con variables).
- [x] Vista previa obligatoria antes de enviar (RN-16): asunto y cuerpo renderizados. (El boton "Encolar envio" queda deshabilitado hasta previsualizar.)
- [x] Encolar el envio masivo a los alumnos atrasados de la materia (F3.2/RN-15).
- [x] Listar lotes con totales por estado (Pendiente/Enviando/Enviado/Error/Cancelado).
- [x] Ver el detalle de un lote por destinatario con su estado.
- [x] Aprobar un lote (RN-17), restringido a `comunicacion:aprobar`.
- [x] Cancelar un lote y/o cancelar un destinatario individual.
- [x] Seguimiento (tracking) de estados con refresco (lotes y detalle con `refetchInterval`).
- [x] Confirmacion clara de exito/errores con Toast.
- [x] Respetar alcance por rol/permiso (enviar vs aprobar).

## Permisos esperados

- [x] Frontend protege `/docente/comunicaciones` con `comunicacion:enviar` (menu lateral + sistema de permisos).
- [x] Las acciones de aprobar/cancelar lote se muestran solo con `comunicacion:aprobar` (`useSession().hasPermission`).
- [x] Backend `preview`/`enviar`/`lotes` usan `comunicacion:enviar` (verificado en el router).
- [x] Backend `lotes/{id}/aprobar`, `lotes/{id}/cancelar`, `{id}/cancelar` usan `comunicacion:aprobar` (verificado).

## Campos esperados

### Composicion

- [x] Materia (selector legible, no UUID).
- [x] Asunto.
- [x] Cuerpo.
- [x] Variables soportadas visibles para el usuario (`{{nombre}}`, `{{apellido}}`, `{{materia}}`, `{{comision}}`).

### Preview

- [x] Asunto renderizado.
- [x] Cuerpo renderizado.

### Lotes

- [x] Materia legible del lote.
- [x] Fecha de creacion.
- [x] Totales por estado.
- [x] Total de destinatarios del lote.

### Detalle de lote

- [x] Destinatario (desencriptado por backend).
- [x] Estado por destinatario.
- [x] Mensaje de error si fallo (columna de estado; el backend expone el error por comunicacion).

## Flujo FL-04

- [x] Parte A — generacion: el docente compone, previsualiza y encola el envio masivo.
- [x] Parte B — aprobacion: un usuario con `comunicacion:aprobar` aprueba o cancela el lote (o por destinatario).
- [x] Parte C — seguimiento: panel de estado por lote/destinatario con refresco.

## Estado actual observado (hallazgos, ya corregidos)

- [x] La ruta y el menu existen y piden `comunicacion:enviar`.
- [x] El frontend de preview enviaba `{tipo, destinatarios, template}` pero el backend espera `{asunto, cuerpo, variables}` → preview rota. **Corregido.**
- [x] El frontend de enviar esperaba `{envio_id, estado, total_destinatarios}` pero el backend devuelve `{lote_id, mensajes_creados}` → respuesta desalineada. **Corregido.**
- [x] El tracking consumia `GET /comunicaciones/{id}/tracking`, endpoint que NO existe en el backend (el real es `/lotes` y `/lotes/{id}`). **Corregido: se eliminó y se usa `/lotes`.**
- [x] No existia UI para listar lotes, ver totales por estado, aprobar ni cancelar. **Agregada (`LotesPanel` + `LoteDetalle`).**
- [x] La pantalla usaba `Alert` en lugar del `Toast` compartido. **Migrada a `Toast`.**
- [x] El formulario pedia destinatarios por texto libre y tipo email/sms/whatsapp, datos que el backend ignora. **Eliminados; el envio deriva destinatarios de atrasados.**

## UX/UI esperada

- [x] Respetar criterios transversales en `revisiones/criterios-transversales-ux-ui.md`.
- [x] Usar Toast compartido para errores y exitos, con cierre automatico a los 5 segundos.
- [x] No usar `alert`, `confirm` ni prompts nativos del navegador.
- [x] Acciones destructivas (cancelar lote) con modal de confirmacion que explique entidad y consecuencia (`ConfirmDialog`).
- [x] Estados de loading, vacio y error claros.
- [x] No mostrar UUID ni IDs tecnicos cuando exista nombre legible (materia por nombre, destinatario desencriptado).
- [x] Botones de accion con icono/tooltip o `aria-label`.
- [x] No dejar logs de debug en consola.

## Reglas de negocio

- [x] RN-16: no hay envio sin preview y confirmacion explicita (boton de envio deshabilitado hasta previsualizar).
- [x] RN-15: los estados y transiciones reflejan Pendiente/Enviando/Enviado/Error/Cancelado (`EstadoBadge` + totales del lote).
- [x] RN-17: el envio masivo permanece Pendiente hasta aprobacion por `comunicacion:aprobar` (backend + gating de UI).
- [x] Envio, aprobacion y cancelacion deben auditarse (RN-23). (Bug de auditoria de `ComunicacionService` corregido; cubierto por `TestAuditoriaComunicaciones`. Ver "Hallazgo critico".)
- [x] Destinatarios cifrados en reposo (backend `encrypt_sensitive_value`, verificado por `TestCifrado`).
- [x] La identidad debe salir siempre de la sesion JWT, no de parametros (routers usan `current_user`).
- [x] Todo query debe filtrar por `tenant_id` (`ComunicacionRepository` recibe `tenant_id` y filtra).

## Pendientes para resolver en orden

1. [x] Realinear tipos y servicios del frontend con el backend real (preview, enviar, lotes, detalle, aprobar, cancelar).
2. [x] Simplificar el formulario: materia + asunto + cuerpo + ayuda de variables; quitar destinatarios libres y tipo.
3. [x] Preview obligatorio antes de enviar (RN-16).
4. [x] Panel de lotes con totales por estado y refresco.
5. [x] Detalle de lote por destinatario.
6. [x] Aprobar/cancelar lote y cancelar destinatario, gated por `comunicacion:aprobar`.
7. [x] Toast compartido y modal de confirmacion para cancelaciones.
8. [x] Corregir el bug de auditoria de `ComunicacionService` (mismo patron que `AnalisisService`).

## Hallazgo critico — RESUELTO (dominio CRITICO: audit log)

`ComunicacionService._registrar_auditoria` tenia el **mismo bug** que `AnalisisService`: importaba `app.models.audit` (inexistente), usaba columnas `recurso_id`/`recurso_tipo` que no existen y envolvia todo en `except (ImportError, Exception): pass`. Resultado: envio/aprobacion/cancelacion **no auditaban** (incumplia RN-23 y SRS §Comunicaciones).

**Correccion aplicada** (con aprobacion del usuario): import a `app.models.audit_log.AuditLog`, mapeo a columnas reales (el recurso lote/comunicacion se preserva en `detalle`; `materia_id` solo cuando el recurso es materia), sin tragar excepciones. Tests TDD sin mock de DB: `TestAuditoriaComunicaciones` (envio → COMUNICACION_ENVIAR, aprobacion → COMUNICACION_APROBAR, cancelacion → COMUNICACION_CANCELAR). **3 passed.**

> Hallazgo adicional (no bloqueante, requiere decision): `enviar_masivo` usa el mismo `usuario_id` para `Comunicacion.enviado_por_id` (FK→`usuarios`) y para el actor de auditoria (FK→`auth_users`), que son entidades distintas. En produccion el router pasa el id de `auth_users`, por lo que `enviado_por_id` podria violar su FK. Conviene separar "actor de sesion" (auth user) de "remitente" (Usuario del dominio) en una iteracion futura. Documentado para no perderlo.
