## Why

La coordinación necesita centralizar programas oficiales de materias y fechas académicas por materia/cohorte para operar el período académico con información única, trazable y reutilizable en el LMS. C-17 completa el soporte backend de estructura documental y calendario académico sobre la base ya implementada de estructura académica, usuarios y permisos.

## What Changes

- Agrega gestión de programas de materia asociados a materia × carrera × cohorte, con referencia de archivo opaca al almacenamiento.
- Agrega gestión de fechas académicas para parciales, TP, coloquios y recuperatorios por materia × cohorte × número/periodo.
- Expone `/api/programas` para cargar/asociar programas y consultar programas vigentes por contexto académico.
- Expone `/api/fechas-academicas` para CRUD, listado tabular y consulta orientada a calendario.
- Agrega generación de fragmento de contenido listo para publicar manualmente en el aula virtual del LMS.
- Protege endpoints con `estructura:gestionar`, identidad desde JWT y aislamiento multi-tenant.
- Agrega migración dedicada para `programa_materia` y `fecha_academica`.

## Capabilities

### New Capabilities
- `programas-materia`: Gestión de documentos de programa oficial por materia, carrera y cohorte con referencia de archivo opaca.
- `fechas-academicas`: Gestión de calendario académico de evaluaciones y generación de fragmentos publicables en LMS.

### Modified Capabilities

No se modifican requisitos de capacidades existentes.

## Impact

- Backend: modelos, schemas, repositories, services y routers para programas y fechas académicas.
- Base de datos: migración Alembic para `programa_materia` y `fecha_academica`, con tenant isolation, soft delete, FKs e índices por contexto académico.
- Seguridad: endpoints autenticados con JWT y guard `estructura:gestionar`; tenant e identidad siempre desde sesión.
- Integración LMS: salida textual/HTML generada para copia manual; no se agrega integración automática con Moodle en este change.
- Tests: CRUD, asociaciones materia×carrera×cohorte, referencia opaca, aislamiento tenant, filtros/listado calendario y fragmento LMS.
