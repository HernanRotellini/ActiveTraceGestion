# SRS / Manual Funcional — activia-trace

## 1. Propósito del documento

Este documento consolida en una sola guía funcional el alcance de **activia-trace** para que el dueño del producto y los usuarios clave puedan revisar qué hace el sistema, qué pantallas contempla, qué datos maneja, qué flujos cubre y qué puntos todavía requieren validación.

No está escrito como documento técnico de implementación. Resume, en lenguaje de negocio, la información proveniente del PRD, la arquitectura, la base de conocimiento, el roadmap `CHANGES.md`, los specs OpenSpec vigentes y las rutas frontend implementadas/intencionadas. Cuando las fuentes documentales entran en conflicto, el conflicto se explicita para que sea revisado.

El objetivo práctico es responder:

- Qué problema resuelve el producto.
- Qué roles usan el sistema y para qué.
- Qué módulos y pantallas existen o están previstos.
- Qué datos se registran y cómo se relacionan.
- Qué reglas de negocio son críticas.
- Qué está especificado/implementado según roadmap y qué debe revisarse funcionalmente.
- Qué preguntas abiertas deberían cerrarse con producto, coordinación, administración o finanzas.

## 2. Visión general del sistema

**activia-trace** es una plataforma de gestión académica y trazabilidad de actividades estudiantiles. Funciona como una capa de inteligencia y operación sobre **Moodle**, que sigue siendo el LMS institucional y fuente primaria de calificaciones, entregas, padrones y reportes de actividad.

El sistema no busca reemplazar Moodle. Moodle conserva el material didáctico, las aulas virtuales y las entregas de los alumnos. activia-trace toma esos datos, los consolida y habilita acciones que Moodle no resuelve por sí solo: detectar atrasos, comunicar recordatorios personalizados, coordinar equipos docentes, organizar encuentros y coloquios, administrar tareas internas, liquidar honorarios y auditar toda acción relevante.

La promesa central es: **que ningún alumno se pierda y ningún docente se quede atrás por falta de información**.

El producto es **multi-tenant**: cada institución opera como un tenant aislado, con su propia estructura académica, usuarios, roles, permisos, plantillas, escalas y grillas salariales. Los datos de un tenant nunca deben cruzarse con los de otro.

El concepto de **trace** es fundacional: toda acción significativa debe quedar registrada con actor, tenant, contexto, fecha/hora, resultado y, cuando corresponda, filas afectadas, IP y agente de usuario. Esta trazabilidad aplica a importaciones, comunicaciones, cambios de permisos, asignaciones, cierres de liquidación, impersonación y operaciones administrativas.

## 3. Actores y roles

Los roles del sistema representan funciones de negocio, no jerarquías acumulativas. Un usuario puede tener más de un rol, y sus permisos efectivos surgen de la unión de esos roles, acotada por su tenant y por la vigencia de sus asignaciones.

| Rol | Responsabilidad principal | Pantallas típicas |
|-----|---------------------------|-------------------|
| **ALUMNO** | Consultar su propio estado académico, confirmar avisos, reservar instancias de evaluación cuando el portal alumno esté disponible. | Portal alumno previsto, avisos pendientes, reserva de coloquios. En el frontend actual no se observa una ruta dedicada de portal alumno. |
| **TUTOR** | Acompañar seguimiento de alumnos, ver atrasos de materias asignadas, registrar/consultar guardias, asistir a profesores. | Monitor docente/tutor, entregas sin corregir, encuentros/guardias, tareas asignadas. |
| **PROFESOR** | Operar sus comisiones: importar calificaciones, configurar umbrales, detectar atrasados, comunicar recordatorios, gestionar encuentros, responder mensajes y tareas. | Mis Comisiones, Entregas sin corregir, Comunicaciones, Monitor, Encuentros, Tareas. |
| **COORDINADOR** | Supervisar cohortes/materias/equipos, clonar equipos, publicar avisos, administrar tareas, monitorear actividad y aprobar comunicaciones masivas. | Equipos docentes, Avisos, Tareas internas, Encuentros, Coloquios, Setup cuatrimestre, Monitor general, Auditoría con alcance propio/global según permiso. |
| **NEXO** | Rol de enlace transversal con tratamiento contable propio. Su semántica operativa todavía requiere validación funcional. | Puede aparecer en liquidaciones y en matriz de roles; no hay pantallas exclusivas claramente especificadas. |
| **ADMIN** | Administrar estructura académica, usuarios, configuración y auditoría del tenant. Supervisa capacidades del sistema. | Admin estructura, Admin usuarios, Admin auditoría, Log auditoría, y acceso amplio a módulos de gestión. |
| **FINANZAS** | Mantener grilla salarial, calcular/cerrar liquidaciones, gestionar facturas, revisar información financiera auditada. | Liquidaciones, Historial, Grilla salarial, Facturas. |

Regla clave: la identidad, el tenant y los roles del usuario salen exclusivamente de la sesión autenticada. Ningún parámetro de URL, body, query string o header puede cambiar quién es el usuario ni qué tenant opera.

## 4. Mapa general de módulos

| Módulo | Propósito | Usuarios principales | Datos principales | Acciones clave |
|--------|-----------|----------------------|-------------------|----------------|
| Auth, sesión y perfil | Permitir acceso seguro al sistema, recuperación, 2FA, logout y edición de perfil propio. | Todos los usuarios autenticados. | Usuario, sesión, refresh token, datos personales/bancarios. | Login, desafío 2FA, recuperar/restablecer contraseña, logout, editar perfil, consultar permisos. |
| Tenancy, RBAC y usuarios | Aislar instituciones y administrar usuarios, roles y permisos finos. | ADMIN, eventualmente soporte. | Tenant, Usuario, Rol, Permiso, RolPermiso, Asignación. | Alta/edición/desactivación de usuarios, asignar roles, proteger rutas/endpoints, fail-closed. |
| Estructura académica | Mantener carreras, cohortes, materias y relación académica base. | ADMIN, COORDINADOR según alcance. | Carrera, Cohorte, Materia. | ABM de carreras/cohortes/materias, filtros, estados activo/inactivo. |
| Padrón, importación Moodle y calificaciones | Incorporar datos académicos desde Moodle WS o archivos. | PROFESOR, COORDINADOR, ADMIN. | VersionPadron, EntradaPadron, Calificacion, UmbralMateria. | Importar padrón con preview, importar calificaciones, importar reporte de finalización, configurar umbral, vaciar datos propios. |
| Monitor, atrasados y entregas | Transformar datos importados en seguimiento accionable. | PROFESOR, TUTOR, COORDINADOR, ADMIN. | Calificaciones, actividades, padrón activo, reportes agregados. | Ver atrasados, ranking, reportes rápidos, notas finales, exportar TPs sin corregir, monitor general y propio. |
| Comunicaciones salientes | Enviar recordatorios personalizados a alumnos con control institucional. | PROFESOR, COORDINADOR, ADMIN. | Comunicacion, lote_id, estado, destinatario cifrado, plantillas. | Preview obligatorio, encolar envío, aprobar/cancelar lote, tracking de estados, despacho worker. |
| Equipos docentes | Gestionar asignaciones, jerarquía y vigencia de docentes por contexto académico. | COORDINADOR, ADMIN, docentes en consulta propia. | Asignacion, Usuario, Materia, Carrera, Cohorte, comisiones. | Ver mis equipos, asignación masiva, clonar equipo, modificar vigencia, exportar. |
| Encuentros y guardias | Planificar clases/reuniones sincrónicas, registrar instancias y guardias. | PROFESOR, TUTOR, COORDINADOR, ADMIN. | SlotEncuentro, InstanciaEncuentro, Guardia. | Crear encuentro recurrente/unico, editar instancia, registrar video, generar HTML para Moodle, consultar guardias. |
| Coloquios y evaluaciones | Gestionar convocatorias, turnos, reservas, cupos y resultados. | COORDINADOR, ADMIN, PROFESOR; ALUMNO para reserva prevista. | Evaluacion, TurnoEvaluacion, ConvocatoriaAlumno, ReservaEvaluacion, ResultadoEvaluacion. | Crear convocatoria, importar alumnos, listar métricas, reservar turno, registrar resultados, consultar agenda. |
| Tareas internas | Coordinar trabajo interno entre docentes y coordinación. | PROFESOR, TUTOR, COORDINADOR, ADMIN. | Tarea, ComentarioTarea. | Crear tarea, ver mis tareas, listar global, delegar, cambiar estado, comentar. |
| Avisos y acknowledgments | Publicar avisos institucionales segmentados y auditar confirmación de lectura. | COORDINADOR, ADMIN; todos como lectores. | Aviso, AcknowledgmentAviso. | Crear avisos, filtrar por scope, confirmar lectura, consultar pendientes, ver estadísticas. |
| Programas y fechas académicas | Centralizar programas oficiales y calendario académico. | COORDINADOR, ADMIN. | ProgramaMateria, FechaAcademica. | Subir/listar/reemplazar programas, registrar fechas de parciales/TP/coloquios, generar contenido para LMS. |
| Liquidaciones, honorarios, grilla y facturas | Calcular honorarios, separar facturantes, cerrar snapshots inmutables. | FINANZAS, ADMIN. | SalarioBase, SalarioPlus, MateriaPlus, Liquidacion, Factura. | Configurar grilla, mapear materia a plus, calcular preview, cerrar liquidación, consultar historial, gestionar facturas. |
| Auditoría y métricas | Supervisar uso, investigar acciones y revisar trazabilidad. | ADMIN, COORDINADOR, FINANZAS según permisos. | AuditLog, métricas por acción/docente/materia. | Ver acciones por día, estado de comunicaciones, interacciones, últimas acciones, log completo con filtros. |
| Mensajería interna | Conversaciones entre usuarios registrados del sistema. | Docentes, coordinación, admin. | Hilos, participantes, mensajes. | Listar inbox, abrir hilo, responder, iniciar conversación. |
| Frontend shell/admin screens | Proveer SPA con menú adaptado a permisos, guards y páginas por feature. | Todos. | Sesión frontend, permisos, rutas. | Navegación, guards de autenticación/autorización, 403/404, cliente HTTP con refresh. |

## 5. Mapa de pantallas frontend

Las rutas siguientes fueron detectadas en `frontend/src/routes/index.tsx` y `frontend/src/layouts/MainLayout.tsx`. Algunas capacidades documentadas en PRD/KB (por ejemplo portal alumno completo, perfil/mensajería visible desde menú) no aparecen como rutas frontend actuales, por lo que deben revisarse como pendientes o provisionales.

### Public/auth

| URL | Propósito | Roles/permisos | Datos mostrados | Acciones |
|-----|-----------|----------------|-----------------|----------|
| `/login` | Inicio de sesión con código de tenant, email y contraseña. | Público no autenticado. | Formulario de credenciales, errores de validación/rate limit. | Login; redirige al dashboard o a 2FA. |
| `/auth/2fa` | Desafío TOTP cuando el usuario tiene 2FA habilitado. | Usuario con `challenge_token`. | Campo de código TOTP. | Validar 2FA, crear sesión, volver a login si no hay desafío. |
| `/auth/recuperar` | Solicitud de recuperación de contraseña. | Público. | Formulario de email y mensaje anti-enumeración. | Solicitar token de recuperación. |
| `/auth/restablecer` | Restablecer contraseña usando token. | Público con token válido. | Formulario de nueva contraseña/confirmación. | Cambiar contraseña, redirigir a login. |
| `/403` | Acceso denegado. | Autenticado sin permiso requerido. | Mensaje de falta de permisos. | Volver a una sección permitida. |
| `/404` y `*` | Ruta inexistente. | Cualquiera. | Mensaje de ruta no encontrada. | Navegar a una sección válida. |

### Inicio/dashboard

| URL | Propósito | Roles/permisos | Datos mostrados | Acciones |
|-----|-----------|----------------|-----------------|----------|
| `/` | Página inicial autenticada. | Cualquier usuario autenticado. | Mensaje de bienvenida y menú lateral filtrado por permisos. | Seleccionar módulo. |

Actualmente la ruta raíz funciona como shell de navegación. El PRD describe dashboards analíticos y vistas iniciales por rol, pero no se observa una pantalla de dashboard funcional avanzada en las rutas actuales.

### Docente

| URL | Propósito | Roles/permisos | Datos mostrados | Acciones |
|-----|-----------|----------------|-----------------|----------|
| `/docente/comisiones` | Listar comisiones/materias del docente. | `calificaciones:ver`. | Materias/comisiones asignadas, estado de análisis. | Entrar al detalle de comisión. |
| `/docente/comisiones/:id` | Gestionar una comisión concreta. | `calificaciones:ver`. | Calificaciones importadas, actividades, umbral, atrasados, ranking, notas finales. | Importar, configurar umbral, ver reportes, preparar comunicaciones. |
| `/docente/entregas` | Detectar entregas finalizadas sin corregir. | `atrasados:ver`. | Tabla de actividades/alumnos potencialmente pendientes de corrección. | Filtrar/exportar. |
| `/docente/comunicaciones` | Gestionar comunicaciones salientes a alumnos. | `comunicacion:enviar`. | Lotes, estados, preview, destinatarios. | Previsualizar, encolar, seguir estados. |
| `/docente/monitor` | Monitor de seguimiento propio. | `atrasados:ver`. | Alumnos de materias asignadas, actividad, aprobadas, pendientes. | Filtrar por alumno, comisión, regional, actividad. |

### Coordinación

| URL | Propósito | Roles/permisos | Datos mostrados | Acciones |
|-----|-----------|----------------|-----------------|----------|
| `/coordinacion/equipos-docentes` | Listar y gestionar equipos docentes. | `equipos:ver`. | Asignaciones, docentes, roles, vigencias, filtros. | Ver detalle; si tiene permiso, crear/editar. |
| `/coordinacion/equipos-docentes/nuevo` | Crear asignación/equipo. | `equipos:gestionar`. | Formulario de asignación. | Alta individual o masiva según pantalla. |
| `/coordinacion/equipos-docentes/:id` | Ver detalle de equipo/asignación. | `equipos:ver`. | Datos de docente, materia, cohorte, rol, vigencia. | Consultar o navegar a edición. |
| `/coordinacion/equipos-docentes/:id/editar` | Editar equipo/asignación. | `equipos:gestionar`. | Formulario precargado. | Modificar vigencia, rol, contexto. |
| `/coordinacion/avisos` | Administrar avisos institucionales. | `avisos:ver`. | Avisos por alcance, severidad, vigencia, ack. | Ver, filtrar; crear/editar si tiene permiso. |
| `/coordinacion/avisos/nuevo` | Crear aviso. | `avisos:gestionar`. | Formulario de título, cuerpo, alcance, severidad, fechas, ack. | Publicar aviso. |
| `/coordinacion/avisos/:id` | Ver detalle de aviso. | `avisos:ver`. | Contenido, destinatarios, estado, estadísticas. | Confirmar o revisar según rol. |
| `/coordinacion/avisos/:id/editar` | Editar aviso. | `avisos:gestionar`. | Formulario precargado. | Modificar/desactivar aviso. |
| `/coordinacion/tareas` | Listar tareas internas. | `tareas:ver`. | Tareas asignadas/globales según permiso, estado, comentarios. | Filtrar, abrir, crear si tiene permiso. |
| `/coordinacion/tareas/nuevo` | Crear tarea. | `tareas:gestionar`. | Formulario de descripción, asignado, materia/contexto. | Crear tarea. |
| `/coordinacion/tareas/:id` | Ver detalle de tarea. | `tareas:ver`. | Estado, responsable, comentarios. | Comentar, revisar. |
| `/coordinacion/tareas/:id/editar` | Editar tarea. | `tareas:gestionar`. | Formulario de tarea. | Cambiar estado, reasignar/delegar. |
| `/coordinacion/encuentros` | Listar encuentros. | `encuentros:ver`. | Encuentros programados/realizados/cancelados con filtros. | Consultar detalle. |
| `/coordinacion/encuentros/:id` | Ver detalle de encuentro. | `encuentros:ver`. | Instancia, estado, meet, grabación, comentario. | Editar según permiso/capacidad. |
| `/coordinacion/coloquios` | Listar convocatorias de coloquio. | `coloquios:ver`. | Convocatorias, turnos, cupos, reservas, métricas. | Abrir convocatoria. |
| `/coordinacion/coloquios/:id` | Ver detalle de convocatoria. | `coloquios:ver`. | Turnos, alumnos convocados, reservas, resultados. | Gestionar resultados/cupos según permiso. |
| `/coordinacion/setup-cuatrimestre` | Preparar inicio de período. | `estructura:gestionar`. | Periodo/cohorte, equipos a clonar, estructura. | Crear cohorte, clonar equipo, ajustar setup. |
| `/coordinacion/monitores` | Monitor general transversal. | `atrasados:ver`. | Alumnos del tenant, actividad, atrasos, filtros por fecha/materia/regional. | Filtrar/exportar/analizar. |

### Liquidaciones/finanzas

| URL | Propósito | Roles/permisos | Datos mostrados | Acciones |
|-----|-----------|----------------|-----------------|----------|
| `/liquidaciones` | Vista del período actual. | `liquidaciones:ver`. | Segmentos General, NEXO y Facturantes; KPIs total sin/con factura; filtros por cohorte/mes/docente. | Ver preview, exportar, cerrar si corresponde. |
| `/liquidaciones/historial` | Consultar liquidaciones cerradas. | `liquidaciones:ver`. | Períodos cerrados y detalles solo lectura. | Buscar/abrir detalle. |
| `/liquidaciones/grilla-salarial` | Configurar salarios base, plus y mapeos. | `liquidaciones:gestionar` en frontend; specs también mencionan `liquidaciones:configurar-salarios`. | Base por rol, plus por clave/rol, vigencias, materia→plus. | ABM de grilla y plus. |
| `/liquidaciones/facturas` | Gestionar facturas de docentes facturantes. | `liquidaciones:ver`. | Facturas, docente, período, detalle, archivo, estado. | Filtrar, marcar como abonada. |

Nota de revisión: hay una pequeña diferencia de nomenclatura entre specs y rutas para permisos de grilla (`liquidaciones:configurar-salarios`, `liquidaciones:administrar-grilla` y `liquidaciones:gestionar`). Producto/técnica debería unificar el nombre final.

### Admin estructura

| URL | Propósito | Roles/permisos | Datos mostrados | Acciones |
|-----|-----------|----------------|-----------------|----------|
| `/admin/estructura/carreras` | ABM de carreras. | `estructura:gestionar`. | Código, nombre, estado, filtros. | Crear, editar, desactivar. |
| `/admin/estructura/cohortes` | ABM de cohortes. | `estructura:gestionar`. | Carrera, nombre, año, vigencia, estado. | Crear, editar, desactivar. |
| `/admin/estructura/materias` | ABM de materias. | `estructura:gestionar`. | Código, nombre, carrera/cohorte según vista, estado. | Crear, editar, desactivar. |

### Admin usuarios

| URL | Propósito | Roles/permisos | Datos mostrados | Acciones |
|-----|-----------|----------------|-----------------|----------|
| `/admin/usuarios` | Administrar usuarios del tenant. | `usuarios:gestionar`. | Nombre, email, roles, estado; PII visible u oculta según permisos/backend. | Crear, editar, desactivar, filtrar por rol/nombre/email. |

### Admin auditoría

| URL | Propósito | Roles/permisos | Datos mostrados | Acciones |
|-----|-----------|----------------|-----------------|----------|
| `/admin/auditoria` | Dashboard de auditoría y métricas. | `auditoria:ver`. | Acciones por día, estado de comunicaciones, interacciones, últimas 200 acciones. | Filtrar por fecha, materia, usuario, estado. |
| `/admin/auditoria/log` | Log completo cronológico. | `auditoria:ver`. | Fecha/hora, usuario, materia, acción, filas afectadas, IP, user agent. | Paginación y filtros combinados. |

### Perfil/mensajería

Los specs backend contemplan `/api/v1/perfil` y `/api/v1/inbox`, pero en las rutas frontend actuales no se observan páginas dedicadas como `/perfil` o `/inbox`. Debe validarse si estas pantallas faltan, si están integradas en otra sección o si quedaron pendientes.

## 6. Flujos principales end-to-end

### Login y sesión

1. El usuario ingresa a `/login`.
2. Completa código de tenant, email y contraseña.
3. El sistema valida credenciales y resuelve identidad, tenant y roles desde la sesión.
4. Si el usuario tiene 2FA, se lo redirige a `/auth/2fa` para ingresar TOTP.
5. Si la autenticación se completa, se guardan access token y refresh token con rotación.
6. El menú y las rutas visibles se adaptan a los permisos efectivos.
7. Ante logout, se revoca el refresh token, se limpia la sesión local y se vuelve a `/login`.
8. Ante 401 con refresh válido, el cliente HTTP intenta renovar tokens; ante refresh fallido, limpia sesión.

### Import/ingest académico desde Moodle, padrón y calificaciones

1. El docente o coordinador selecciona materia/cohorte/comisión.
2. El sistema puede sincronizar con Moodle Web Services o aceptar archivo `.xlsx`/`.csv` como fallback.
3. Para padrón, se realiza preview con columnas detectadas y total de filas.
4. Al confirmar, se crea una nueva `VersionPadron`, queda activa y se desactiva la anterior del mismo contexto sin borrarla.
5. Para calificaciones, se detectan columnas numéricas `(Real)` y valores textuales aprobatorios.
6. El usuario selecciona actividades a incluir.
7. Se registran calificaciones, origen, fecha de importación y auditoría.
8. Los emails de alumnos y datos sensibles se almacenan cifrados cuando corresponde.

### Detectar atrasos y entregas sin corregir

1. El usuario configura o usa el umbral por defecto del 60%.
2. El sistema cruza padrón activo, actividades importadas y calificaciones.
3. Un alumno queda atrasado si tiene actividad faltante o nota inferior al umbral.
4. El ranking de aprobadas excluye alumnos sin ninguna actividad aprobada.
5. Para entregas sin corregir, se cruza el reporte de finalización de Moodle con calificaciones importadas.
6. Solo se listan entregas de escala textual sin calificación, porque en escala numérica la ausencia de nota se interpreta diferente.
7. El usuario puede filtrar y exportar listados.

### Crear, aprobar y enviar comunicaciones

1. El docente selecciona alumnos atrasados o una materia con atrasados.
2. Define asunto y cuerpo con variables como `{{nombre}}`, `{{materia}}`, `{{comision}}`.
3. El sistema muestra preview renderizado. No se permite envío sin preview.
4. Al confirmar, se crea un mensaje por alumno en estado `Pendiente`, agrupado por `lote_id`.
5. Si el tenant requiere aprobación, el worker no despacha hasta que un usuario con `comunicacion:aprobar` apruebe.
6. El aprobador puede aprobar o cancelar el lote.
7. El worker procesa `Pendiente → Enviando → Enviado/Error`; también puede quedar `Cancelado`.
8. El panel muestra totales por estado y cada operación audita envío, aprobación o cancelación.

### Gestionar estructura académica

1. ADMIN crea o edita carreras con código único por tenant.
2. ADMIN crea cohortes asociadas a carrera, con nombre, año, vigencia y estado.
3. ADMIN mantiene materias del catálogo único por tenant.
4. Las entidades inactivas se conservan para histórico y no deben borrarse físicamente.
5. Carreras inactivas no deberían admitir nuevas cohortes abiertas.

### Gestionar equipos docentes

1. El coordinador/admin consulta asignaciones existentes.
2. Puede asignar múltiples docentes a materia × carrera × cohorte × rol con vigencia.
3. Puede definir responsables jerárquicos.
4. Puede clonar asignaciones vigentes de un período/cohorte a otro.
5. Puede modificar vigencia general de un equipo.
6. Los docentes consultan sus propias asignaciones y su estado vigente/vencido.
7. La vigencia condiciona permisos: una asignación vencida no otorga acceso, pero queda histórica.

### Programar encuentros y guardias

1. El profesor/coordinador crea un encuentro recurrente indicando día, hora, fecha de inicio y cantidad de semanas.
2. El sistema genera automáticamente las instancias programadas.
3. También puede crear un encuentro único sin recurrencia.
4. Cada instancia se edita de forma independiente: estado, link de meet, grabación y comentario.
5. El sistema puede generar HTML para copiar manualmente en Moodle.
6. Las guardias se registran para tutor/profesor y pueden consultarse/exportarse.
7. El flujo exacto de alta de guardia requiere validación funcional final, aunque los specs ya contemplan registro.

### Gestionar coloquios, evaluaciones, reservas y resultados

1. Coordinación crea convocatoria indicando materia, cohorte, instancia y turnos con cupos.
2. Importa alumnos convocados.
3. El listado muestra métricas: convocados, reservas activas, cupos totales/libres.
4. El alumno, cuando el portal esté habilitado, reserva un turno disponible.
5. Una convocatoria cerrada no admite nuevas reservas ni importación.
6. ADMIN/coordinación consulta agenda consolidada.
7. ADMIN registra o actualiza resultados finales.
8. El flujo de reserva del alumno aún figura como pregunta abierta en la KB y debe validarse contra la implementación actual.

### Tareas internas

1. Un usuario con permiso crea una tarea con descripción, asignado y contexto opcional.
2. La tarea nace en estado `Pendiente`.
3. El usuario asignado ve sus tareas; coordinación/admin puede ver listado global filtrable.
4. La tarea puede delegarse a otro usuario del mismo tenant.
5. El workflow acepta `Pendiente`, `En progreso`, `Resuelta`, `Cancelada`.
6. Estados terminales no deben reabrirse sin regla explícita.
7. Los comentarios forman un hilo cronológico auditado por autor y fecha.

### Programas y fechas académicas

1. Coordinador/admin sube programa de materia para materia × carrera × cohorte.
2. La referencia de archivo es opaca, no un path local manipulable por usuario.
3. Coordinador/admin registra fechas académicas por materia/cohorte: parcial, TP, coloquio o recuperatorio.
4. Las fechas se presentan en tabla/calendario y pueden servir para generar contenido listo para Moodle.

### Liquidaciones: grilla, preview, cierre y facturas

1. FINANZAS configura salario base por rol con vigencia.
2. FINANZAS configura claves de plus por tenant, valores por rol y vigencia.
3. FINANZAS mapea cada materia a cero o una clave de plus vigente.
4. Para un período `AAAA-MM` y una cohorte, el sistema toma asignaciones vigentes.
5. Calcula `Total = Base(rol) + Σ(Plus(clave, rol) × N_comisiones)`.
6. Si una materia no tiene clave vigente, no suma plus.
7. Los NEXO se muestran separados, pero suman al total general si no son facturantes.
8. Los docentes facturantes se excluyen del total pagable Base+Plus y se gestionan por facturas.
9. La vista muestra preview segmentado y KPIs.
10. Al cerrar, se persiste un snapshot inmutable; cambios futuros de grilla no recalculan liquidaciones cerradas.
11. Las facturas se asocian a docente + período con detalle libre, archivo opaco y estado `Pendiente`/`Abonada`.

### Revisión de auditoría

1. ADMIN/COORDINADOR/FINANZAS acceden según `auditoria:ver`.
2. El dashboard resume acciones por día, comunicaciones por estado e interacciones por docente/materia.
3. El log completo permite filtrar por fechas, materia, usuario y tipo de acción.
4. La auditoría es append-only: no se edita ni borra desde la aplicación.
5. La impersonación, si se usa, debe registrar actor real e impersonado.

## 7. Modelo de datos explicado

El modelo se organiza alrededor de **Tenant**. Todo dato pertenece a una institución y lleva `tenant_id`. Esto permite operar múltiples instituciones en la misma plataforma sin mezclar información.

Las entidades académicas principales son:

- **Carrera**: programa académico, por ejemplo TUPAD.
- **Cohorte**: camada o período de ingreso, por ejemplo MAR-2026 o AGO-2026.
- **Materia**: unidad del catálogo único del tenant.
- **Usuario**: cualquier persona del sistema, identificada por UUID interno, no por legajo.
- **Asignación**: vínculo entre usuario, rol y contexto académico, con vigencia.
- **VersionPadron / EntradaPadron**: versiones de alumnos por materia/cohorte y sus filas.
- **Calificacion / UmbralMateria**: notas, aprobaciones derivadas y criterio de aprobación.
- **SlotEncuentro / InstanciaEncuentro / Guardia**: planificación y registro de encuentros/guardias.
- **Aviso / AcknowledgmentAviso**: comunicación institucional y confirmación de lectura.
- **Evaluacion / ReservaEvaluacion / ResultadoEvaluacion**: coloquios, reservas y resultados.
- **ProgramaMateria / FechaAcademica**: documentos y calendario académico.
- **SalarioBase / SalarioPlus / MateriaPlus / Liquidacion / Factura**: dominio financiero.
- **Comunicacion**: cola e historial de mensajes a alumnos.
- **AuditLog**: registro inmutable de acciones significativas.

Principios de datos:

- `tenant_id` está en todas las entidades de dominio.
- El usuario se identifica por UUID opaco; legajo, DNI, email o CUIL son atributos de negocio.
- DNI, CUIL, CBU, alias, email y destinatarios pueden requerir cifrado en reposo según sensibilidad.
- Soft delete preserva histórico; no se borra físicamente desde operaciones normales.
- Las asignaciones tienen vigencia; una asignación vencida no da permisos pero se conserva.
- El padrón vigente es la última versión activa, pero las versiones anteriores se conservan según specs vigentes.
- La liquidación cerrada es un snapshot inmutable.

## 8. Reglas de negocio críticas

### Seguridad, multi-tenancy y RBAC

- La identidad y el tenant salen solo de la sesión autenticada.
- Todos los endpoints protegidos exigen permisos `modulo:accion`.
- El sistema falla cerrado: sin permiso explícito, responde 403.
- Los repositories filtran por tenant por defecto.
- Ningún query puede cruzar tenants.
- No existe superusuario binario; ADMIN también opera por permisos explícitos.
- Impersonación requiere permiso, sesión distinguible y auditoría completa.
- PII sensible se cifra en reposo y no debe aparecer en logs.

### Importación, atrasados y reportes

- Las columnas numéricas importadas desde Moodle se identifican por encabezado terminado en `(Real)`.
- Valores textuales como `Satisfactorio` y `Supera lo esperado` cuentan como aprobados.
- Umbral por defecto: 60%, configurable por docente/materia.
- Alumno atrasado: actividad faltante o nota inferior al umbral.
- TPs sin corregir: entregas finalizadas en Moodle sin calificación, solo para escala textual.
- Ranking de aprobadas excluye alumnos con cero aprobadas.

### Padrón

Hay conflicto documental:

| Fuente | Regla |
|--------|-------|
| KB antigua (`05_reglas_de_negocio.md` RN-05, `09_decisiones_y_supuestos.md` D4/A4) | El padrón se reemplaza sin conservar historial. |
| PRD, arquitectura, `CHANGES.md`, `openspec/specs/padron-ingesta/spec.md` | El padrón es versionado; cada import crea nueva versión y conserva historial. |

Para este SRS se toma como referencia funcional vigente el modelo **versionado**, porque está en PRD, arquitectura, roadmap completado y specs actuales. El conflicto debe cerrarse formalmente actualizando la KB antigua.

### Comunicaciones

- Preview obligatorio antes de encolar cualquier envío.
- Estados válidos: `Pendiente → Enviando`, `Pendiente → Cancelado`, `Enviando → Enviado`, `Enviando → Error`.
- Transiciones inversas o desde terminales se rechazan.
- Envíos masivos pueden requerir aprobación humana por tenant.
- Destinatarios se almacenan cifrados.
- Envío, aprobación y cancelación generan auditoría.

### Tareas internas

- Estados: `Pendiente`, `En progreso`, `Resuelta`, `Cancelada`.
- `Resuelta` y `Cancelada` son terminales según specs.
- La identidad del creador/asignador se toma de sesión, no del body.
- Comentarios son cronológicos y tenant-scoped.

### Avisos

- Alcances: Global, PorMateria, PorCohorte, PorRol.
- Severidad: Info, Advertencia, Crítico.
- Ventana de vigencia controla visibilidad.
- `requiere_ack` obliga confirmación de lectura.
- Contadores de ack se derivan de registros, no se inventan manualmente.

### Liquidaciones

- Estructura: Base + Plus.
- Base por rol vigente en el mes.
- Plus por clave configurable del tenant, rol y mapeo Materia→clave.
- Plus acumula por cantidad de comisiones activas, sin tope por defecto.
- NEXO se muestra separado pero suma si no es facturante.
- Facturantes se excluyen del total pagable general y se gestionan por facturas.
- La liquidación opera por cohorte × mes.
- Cierre = snapshot inmutable.
- Facturas tienen estado `Pendiente` o `Abonada`.

## 9. Permisos y visibilidad

Los permisos siguen formato `modulo:accion`, por ejemplo:

| Permiso | Uso esperado |
|---------|--------------|
| `calificaciones:ver` / `calificaciones:importar` | Ver/importar datos académicos de comisión. |
| `atrasados:ver` | Ver atrasados, monitores y entregas sin corregir. |
| `comunicacion:enviar` | Crear preview y encolar comunicaciones. |
| `comunicacion:aprobar` | Aprobar/cancelar envíos masivos. |
| `equipos:ver` / `equipos:gestionar` / `equipos:asignar` | Consultar o administrar equipos docentes. |
| `avisos:ver` / `avisos:gestionar` / `avisos:publicar` | Ver o administrar avisos. |
| `tareas:ver` / `tareas:gestionar` | Ver o administrar tareas internas. |
| `encuentros:ver` / `encuentros:gestionar` | Ver o administrar encuentros. |
| `coloquios:ver` / `coloquios:gestionar` | Ver o administrar coloquios. |
| `estructura:gestionar` | Administrar carreras, cohortes y materias. |
| `usuarios:gestionar` | Administrar usuarios del tenant. |
| `liquidaciones:ver` | Ver liquidaciones, historial y facturas. |
| `liquidaciones:gestionar` / `liquidaciones:configurar-salarios` | Administrar grilla salarial y configuraciones. |
| `auditoria:ver` | Ver auditoría y métricas. |
| `impersonacion:usar` | Iniciar suplantación legítima y auditada. |

La visibilidad del menú frontend se filtra por permisos. Una ruta protegida requiere sesión; si falta sesión, redirige a `/login`. Si hay sesión pero faltan permisos, muestra 403.

La matriz base por rol se resume así:

- ALUMNO: estado propio, reserva de evaluación, confirmar avisos.
- TUTOR: seguimiento, atrasados, guardias, avisos, tareas propias.
- PROFESOR: calificaciones propias, atrasados propios, comunicaciones propias, encuentros, tareas.
- COORDINADOR: equipos, avisos, tareas, monitores, aprobación de comunicaciones, auditoría acotada/global según permiso.
- ADMIN: estructura, usuarios, auditoría, configuración, capacidades amplias del tenant.
- FINANZAS: grilla, liquidaciones, facturas, auditoría financiera.
- NEXO: rol definido nominalmente, permisos finales pendientes de validación funcional.

## 10. Integraciones

### Moodle Web Services

Moodle es fuente de verdad académica. activia-trace consume datos de Moodle mediante Web Services y fallback manual.

Datos importados:

- Calificaciones numéricas y textuales.
- Participantes/padrón.
- Actividades evaluativas.
- Reporte de finalización de actividades.

Funciones Moodle previstas incluyen `core_grades_get_grades`, `core_enrol_get_enrolled_users`, `core_user_get_users` y `gradereport_user_get_grade_items`, ajustables según versión del tenant.

La integración es principalmente entrante: el sistema no escribe automáticamente en Moodle. Cuando se necesita publicar contenido en Moodle, genera fragmentos HTML o archivos que el docente copia/importa manualmente.

### N8N

N8N aparece como posible orquestador de flujos externos. La arquitectura también contempla worker propio para comunicaciones. La decisión fina worker propio vs N8N se documenta como punto técnico a validar por módulo.

### Email/comunication worker

El worker asíncrono procesa comunicaciones, cambia estados y registra resultados. En specs actuales el envío real puede estar simulado/stub en etapas tempranas, por lo que debe validarse si ya existe integración real con proveedor de email en ambiente productivo.

### Observabilidad y logging

El sistema debe tener logs estructurados JSON, OpenTelemetry para trazas, y audit log de negocio separado del log técnico.

## 11. Estado de implementación según roadmap

Este estado se basa en `CHANGES.md`, specs actuales y rutas frontend detectadas. No se ejecutaron builds/tests para verificar runtime.

### Implementado / especificado

`CHANGES.md` marca como completados `[x]` los 24 changes principales:

| Fase | Changes marcados completos | Alcance funcional |
|------|----------------------------|-------------------|
| Cimiento | C-01 a C-05 | Foundation, tenancy, auth, RBAC, audit log. |
| Dominio académico base | C-06, C-07, C-08, C-09, C-10, C-11, C-12 | Estructura, usuarios/asignaciones, equipos, padrón/Moodle, calificaciones, análisis, comunicaciones. |
| Módulos paralelos | C-13 a C-20 | Encuentros, coloquios, avisos, tareas, programas/fechas, liquidaciones, auditoría, perfil/mensajería. |
| Frontend | C-21 a C-24 | Shell/auth, frontend docente, coordinación, finanzas/admin. |

Además existen specs vigentes bajo `openspec/specs/` para auth, tenant isolation, encryption, RBAC, usuarios, estructura, padrón, calificaciones, atrasados, comunicaciones, equipos, encuentros, guardias, coloquios, avisos, tareas, programas, fechas, liquidaciones, facturas, auditoría, perfil, mensajería y frontend.

El frontend tiene rutas reales para auth, docente, coordinación, finanzas y admin. Esto indica una cobertura amplia de la interfaz prevista para MVP.

### En desarrollo o pendiente

Aunque el roadmap está marcado completo, hay áreas que el PRD/KB describen como Fase 2 o futuro y que no se observan como rutas completas en el frontend actual:

- Portal alumno completo: estado académico propio, reserva de coloquios desde interfaz alumno, descarga de programas y notificaciones push.
- Analytics avanzado/BI: tendencias longitudinales, predicción de abandono, reportes ejecutivos PDF/Excel.
- API pública externa OpenAPI para terceros, más allá de la API interna.
- App móvil/PWA avanzada, real-time chat docente-alumno, AFIP, i18n.
- Pantallas frontend explícitas de perfil propio e inbox interno, aunque existen specs/API para perfil y mensajería.
- Integración real de email si el worker todavía usa stub de envío.

### Requiere validación funcional

- Confirmar que todas las pantallas listadas están operativas con datos reales y no solo scaffolding/demo.
- Confirmar qué permisos finales usa cada pantalla, especialmente liquidaciones (`liquidaciones:gestionar` vs `liquidaciones:configurar-salarios`).
- Validar la semántica final de NEXO.
- Validar el flujo exacto de guardias.
- Validar cómo reserva coloquio el ALUMNO y si el portal alumno está dentro del MVP o fase posterior.
- Validar que el cambio de padrón a modelo versionado quede reflejado en toda la KB.
- Confirmar proveedor real de email/comunicaciones y política de reintentos.

## 12. Preguntas abiertas y decisiones a revisar

### Preguntas abiertas de alto impacto

| Código | Tema | Estado sugerido |
|--------|------|-----------------|
| PA-01 | Catálogo de materias: Materia vs InstanciaDictado. | La arquitectura cerró ADR-006 como Materia + Dictado, pero la KB de preguntas abiertas aún lo lista. Debe sincronizarse la documentación y validar si el código implementa Dictado o solo Materia. |
| PA-07 | Cohortes pertenecen a carrera o son transversales. | El modelo actual asocia Cohorte a Carrera; validar con negocio si esto cubre todos los casos. |
| PA-25 | Semántica precisa del rol NEXO. | Sigue siendo la pregunta funcional más importante para permisos y pantallas. |

### Liquidaciones y facturas

PA-22, PA-23 y PA-24 aparecen resueltas en la KB actual:

- Claves de Plus configurables por tenant.
- Mapeo Materia→Plus con vigencia.
- Plus acumulado por comisión activa, sin tope por defecto.
- Facturas asociadas a docente + período con detalle libre, sin comisión obligatoria ni validación contra Base+Plus.

Debe validarse con FINANZAS si estas decisiones coinciden con la operatoria real.

### Otras preguntas a revisar

| Tema | Revisión necesaria |
|------|--------------------|
| Guardias | Desde qué pantalla se crean, quién puede crear en nombre de quién y si requieren aprobación. |
| Tareas | Specs cerraron estados, pero KB aún menciona PA-08; sincronizar documentación. |
| Comunicación por grupos en equipos | Definir si es comunicación al equipo docente, entre pares o si requiere aprobación. |
| Monitor general | Definir criterio de clasificación configurable y si afecta reglas o solo vista. |
| Encuentros admin | Confirmar si coordinación puede editar/crear en nombre de docentes o solo consultar. |
| Reserva de coloquios | Confirmar canal: dentro del sistema, Moodle o link externo. |
| Severidad de avisos | Confirmar si severidad tiene solo efecto visual o bloquea/notifica. |
| CUIL | Confirmar si se calcula, se carga manualmente o lo gestiona ADMIN. |
| Desactivación de docentes | Definir qué ocurre con asignaciones vigentes. |

## 13. Checklist de revisión para el usuario

### Roles y permisos

- Confirmar si los roles ALUMNO, TUTOR, PROFESOR, COORDINADOR, NEXO, ADMIN y FINANZAS son correctos.
- Confirmar si un usuario puede tener varios roles simultáneos.
- Revisar qué puede hacer exactamente NEXO.
- Revisar quién aprueba comunicaciones masivas.
- Revisar si FINANZAS necesita acceso a auditoría general o solo financiera.

### Pantallas

- Revisar si el menú detectado cubre todas las áreas necesarias.
- Confirmar si falta pantalla de perfil propio.
- Confirmar si falta inbox/mensajería interna.
- Confirmar si se necesita portal alumno en MVP.
- Confirmar si dashboard inicial debe ser más que una bienvenida.

### Datos

- Revisar campos obligatorios de usuario/docente: email, DNI, CUIL, banco, CBU, alias, regional, modalidad de cobro.
- Validar estructura Carrera → Cohorte → Materia.
- Confirmar nomenclatura de comisiones y cohortes.
- Confirmar qué PII debe verse en pantalla y quién puede verla.

### Importaciones y análisis

- Validar formatos reales de exportación Moodle.
- Validar columnas `(Real)` y escalas textuales aprobatorias.
- Confirmar si el padrón debe conservar historial versionado.
- Probar casos de alumnos sin cuenta de usuario.
- Revisar cómo se calculan atrasados y notas finales.

### Comunicaciones y avisos

- Revisar plantillas y variables permitidas.
- Confirmar si toda comunicación masiva requiere aprobación o si es configurable por tenant.
- Validar estados de comunicaciones y mensajes de error.
- Revisar severidades de avisos y comportamiento de ack.

### Equipos, encuentros y tareas

- Validar clonado de equipos entre cohortes.
- Revisar vigencias y responsables jerárquicos.
- Confirmar flujo de alta/edición de guardias.
- Confirmar estados de encuentros.
- Validar workflow de tareas y quién puede cerrarlas/cancelarlas.

### Coloquios

- Confirmar quién crea convocatorias.
- Confirmar cómo se importan convocados.
- Confirmar si alumnos reservan desde activia-trace.
- Validar reglas de cupos, cancelación y cierre.
- Confirmar quién registra resultados.

### Liquidaciones

- Revisar roles con base salarial: PROFESOR, TUTOR, NEXO, COORDINADOR.
- Validar claves de Plus y mapeo a materias.
- Confirmar acumulación por comisión y ausencia de tope.
- Confirmar tratamiento de NEXO.
- Confirmar flujo de facturantes y facturas.
- Validar que cierre sea irreversible.

### Auditoría

- Revisar acciones que deben auditarse obligatoriamente.
- Validar filtros y retención del log.
- Confirmar si impersonación se habilita en MVP.
- Confirmar qué datos de IP/user agent se requieren.

## 14. Apéndice: glosario

| Término | Definición |
|---------|------------|
| **Tenant** | Institución aislada dentro del sistema. Tiene sus propios usuarios, datos, permisos y configuración. |
| **Multi-tenant** | Modelo donde varias instituciones usan la misma plataforma sin compartir datos entre sí. |
| **Cohorte** | Grupo/camada de alumnos asociado a un período de ingreso o cursado, por ejemplo MAR-2026. |
| **Carrera** | Programa académico, por ejemplo TUPAD. |
| **Materia** | Unidad académica del catálogo del tenant. |
| **Comisión** | Grupo operativo de cursado dentro de una materia/cohorte. |
| **Dictado** | Instancia concreta de una materia en carrera × cohorte. Aparece como decisión arquitectónica, pero debe validarse su representación final en código/dominio. |
| **Legajo** | Identificador institucional de una persona. En activia-trace es atributo de negocio, no credencial ni identidad técnica. |
| **Moodle** | LMS institucional y fuente de datos académicos. |
| **Moodle Web Services** | API de Moodle usada para sincronizar calificaciones, usuarios, actividades y reportes. |
| **Padrón** | Listado de alumnos participantes de una materia/cohorte/comisión. |
| **VersionPadron** | Versión histórica de un padrón importado. Solo una versión está activa por contexto. |
| **Umbral** | Porcentaje mínimo para considerar aprobada una actividad numérica; por defecto 60%. |
| **Atrasado** | Alumno con actividad faltante o nota inferior al umbral. |
| **Entrega sin corregir** | Actividad marcada como finalizada en Moodle pero sin calificación registrada en activia-trace. |
| **RBAC** | Control de acceso basado en roles y permisos finos. |
| **Permiso `modulo:accion`** | Capacidad atómica, por ejemplo `comunicacion:aprobar`. |
| **Fail-closed** | Si no hay permiso explícito o hay ambigüedad, se deniega acceso. |
| **Soft delete** | Baja lógica: el registro se marca como eliminado/inactivo, pero no se borra físicamente. |
| **PII** | Información personal sensible, como DNI, CUIL, CBU o email. |
| **NEXO** | Rol de enlace transversal con tratamiento contable propio; su función operativa exacta requiere validación. |
| **Plus** | Adicional salarial configurable por clave de materia y rol. |
| **Grilla salarial** | Configuración de bases y plus con vigencia temporal. |
| **Liquidación** | Cálculo de honorarios de docentes para una cohorte y mes. |
| **Facturante** | Docente que cobra mediante factura y queda fuera del total pagable Base+Plus general. |
| **Factura** | Comprobante asociado a docente y período, con estado pendiente o abonada. |
| **Snapshot** | Copia inmutable de datos calculados al cerrar una liquidación. |
| **Audit log** | Registro inmutable de acciones significativas del sistema. |
| **Impersonación** | Suplantación legítima y auditada de un usuario por soporte/admin autorizado. |
| **Acknowledgment / ACK** | Confirmación explícita de lectura de un aviso. |
| **Worker** | Proceso asíncrono que despacha comunicaciones fuera del ciclo de request del usuario. |
