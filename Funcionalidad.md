# Funcionalidad del Sistema — activia-trace

> Mapa de pantallas, funcionalidad breve y roles con acceso.
> Si un rol no tiene acceso a una herramienta, no la ve en el menú lateral ni puede acceder a su ruta.

---

## Módulo de Autenticación (`/login`, `/auth/*`)

| Pantalla | Funcionalidad | Acceso |
|----------|---------------|--------|
| **Inicio de Sesión** | Login con código de institución + email + contraseña. Soporta segundo factor (2FA). | Público |
| **Desafío 2FA** | Ingreso de código TOTP de 6 dígitos. | Público (con challenge activo) |
| **Recuperar Contraseña** | Solicitud de restablecimiento por email. | Público |
| **Restablecer Contraseña** | Cambio de contraseña mediante token. | Público (con token válido) |

---

## Módulo Docente

### Mis Comisiones (`/docente/comisiones`)
Lista las comisiones asignadas al docente. Cada una abre un detalle con pestañas: calificaciones, importar notas, umbral, atrasados, ranking, notas finales, reportes.
> **Roles:** TUTOR, PROFESOR, COORDINADOR, ADMIN

### Entregas sin Corregir (`/docente/entregas`)
Lista entregas de alumnos pendientes de corrección. Filtro por comisión. Exportación.
> **Roles:** TUTOR, PROFESOR, COORDINADOR, ADMIN

### Comunicaciones (`/docente/comunicaciones`)
Redactar y enviar comunicaciones masivas (email/SMS/WhatsApp). Incluye previsualización con sustitución de variables y timeline de seguimiento.
> **Roles:** PROFESOR (scope propio), COORDINADOR, ADMIN, NEXO

### Monitor de Alumnos (`/docente/monitor`)
Tabla filtrable de alumnos con estado de actividades: total, aprobadas, pendientes. Para seguimiento individual.
> **Roles:** TUTOR, PROFESOR, COORDINADOR, ADMIN

---

## Módulo de Coordinación

### Equipos Docentes (`/coordinacion/equipos-docentes`)
CRUD completo de equipos docentes: listado con filtros, creación, edición, detalle con asignación masiva, clonación, cambio de vigencia y exportación CSV.
> **Roles:** COORDINADOR, ADMIN

### Avisos (`/coordinacion/avisos`)
Tablón de avisos institucionales con alcance configurable (Global, PorMateria, PorCohorte, PorRol). Creación, edición, publicación, archivado. Seguimiento de confirmación de lectura (acks).
> **Roles:** COORDINADOR, ADMIN, NEXO

### Tareas Internas (`/coordinacion/tareas`)
Gestión de tareas del equipo: listado con filtros por prioridad/estado, creación, detalle con comentarios y cambio de estado.
> **Roles:** COORDINADOR, ADMIN

### Encuentros (`/coordinacion/encuentros`)
Listado y detalle de encuentros registrados (clases, tutorías). Filtro por fecha.
> **Roles:** COORDINADOR, ADMIN

### Coloquios (`/coordinacion/coloquios`)
Listado y detalle de coloquios. Gestión de reservas, confirmación/cancelación y registro de resultados (aprobado/desaprobado/ausente).
> **Roles:** COORDINADOR, ADMIN

### Setup Cuatrimestre (`/coordinacion/setup-cuatrimestre`)
Gestión de períodos académicos: crear, activar/desactivar cuatrimestres con fechas de inicio y fin.
> **Roles:** COORDINADOR, ADMIN

### Monitor General (`/coordinacion/monitores`)
Dashboard con métricas globales: total alumnos, comisiones, promedio de atraso, entregas pendientes. Desglose por materia con exportación.
> **Roles:** COORDINADOR, ADMIN

---

## Módulo de Finanzas

### Liquidación del Período (`/liquidaciones`)
Liquidación activa del período actual con KPIs, tabla de items (docentes, montos), filtros y botón de cierre.
> **Roles:** FINANZAS, ADMIN

### Historial de Liquidaciones (`/liquidaciones/historial`)
Listado histórico de liquidaciones cerradas con navegación al detalle de cada una.
> **Roles:** FINANZAS, ADMIN

### Grilla Salarial (`/liquidaciones/grilla-salarial`)
Gestión de salarios base y plus salariales. Dos pestañas: Salarios (CRUD) y Plus (CRUD).
> **Roles:** FINANZAS, ADMIN

### Facturas Docentes (`/liquidaciones/facturas`)
Listado de facturas de docentes con filtros, creación y cambio de estado (pendiente/abonada).
> **Roles:** FINANZAS, ADMIN

---

## Módulo de Administración

### Carreras (`/admin/estructura/carreras`)
ABM de carreras: nombre, código, descripción. Creación, edición y eliminación.
> **Roles:** COORDINADOR, ADMIN

### Cohortes (`/admin/estructura/cohortes`)
ABM de cohortes filtrados por carrera: nombre, año.
> **Roles:** COORDINADOR, ADMIN

### Materias (`/admin/estructura/materias`)
ABM de materias filtrados por carrera y cohorte: nombre, código, carga horaria.
> **Roles:** COORDINADOR, ADMIN

### Usuarios (`/admin/usuarios`)
ABM de usuarios del sistema: nombre, email, contraseña, DNI, CBU, asignación de roles (ALUMNO, TUTOR, PROFESOR, COORDINADOR, NEXO, ADMIN, FINANZAS). Soporta visualización de PII.
> **Roles:** ADMIN

### Dashboard de Auditoría (`/admin/auditoria`)
Métricas de actividad del sistema: gráficos de acciones por usuario/materia, tabla del log de auditoría con filtros.
> **Roles:** ADMIN

### Log de Auditoría (`/admin/auditoria/log`)
Log detallado de auditoría con filtros por usuario, materia, acción y rango de fechas. Paginado.
> **Roles:** ADMIN

---

## Resumen de Roles y Módulos Visibles

| Rol | Módulos visibles |
|-----|------------------|
| **ALUMNO** | Sin acceso al frontend de gestión (solo consumen avisos vía API) |
| **TUTOR** | Mis Comisiones, Entregas sin corregir, Monitor |
| **PROFESOR** | Mis Comisiones, Entregas sin corregir, Comunicaciones (scope propio), Monitor |
| **COORDINADOR** | Todo el módulo Docente + Coordinación + Estructura académica |
| **NEXO** | Avisos, Comunicaciones |
| **ADMIN** | Todas las pantallas del sistema |
| **FINANZAS** | Liquidaciones, Grilla salarial, Facturas |
