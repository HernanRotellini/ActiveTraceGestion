## Context

C-17 implementa el backend para F5.3 y F5.4: gestión de programas oficiales y fechas académicas sobre la estructura académica ya existente (`Carrera`, `Cohorte`, `Materia`). El dominio tiene governance BAJO, pero debe respetar las reglas duras del proyecto: Clean Architecture, tenant isolation row-level, `tenant_id` en cada tabla, soft delete, schemas Pydantic v2 con `extra='forbid'`, identidad/tenant exclusivamente desde JWT y guard `estructura:gestionar`.

El alcance incluye persistencia de `ProgramaMateria` y `FechaAcademica`, endpoints CRUD/listado, carga/asociación de programas mediante referencia opaca al almacenamiento y generación de un fragmento de contenido para publicación manual en el LMS.

## Goals / Non-Goals

**Goals:**
- Modelar `ProgramaMateria` como documento oficial por materia × carrera × cohorte con `referencia_archivo` opaca.
- Modelar `FechaAcademica` como evento académico por materia × cohorte, tipo, número, período, fecha y título.
- Exponer `/api/programas` para crear/asociar, listar, consultar, actualizar metadatos y soft-delete programas.
- Exponer `/api/fechas-academicas` para CRUD, filtros tabulares y consulta calendario.
- Generar fragmento HTML/textual listo para copiar al aula virtual del LMS a partir de fechas académicas filtradas.
- Mantener tests TDD con DB real/efímera para CRUD, asociaciones, opacidad de referencias, filtros y aislamiento tenant.

**Non-Goals:**
- No implementar almacenamiento real de archivos ni integración con S3/local filesystem; se persiste solo una referencia opaca.
- No publicar automáticamente en Moodle ni llamar Moodle WS; la salida es para copia manual.
- No implementar UI calendario/frontend; este change es backend.
- No modificar la estructura académica base ni resolver PA-01/PA-07, ya cerradas para C-06 en el enfoque vigente.

## Decisions

### 1. Referencia de archivo opaca, no path de disco

`ProgramaMateria.referencia_archivo` será un string opaco provisto por el cliente/capa de almacenamiento. El backend lo valida como valor presente y lo devuelve sin interpretar estructura de path, bucket o URL firmada.

Alternativa considerada: guardar paths locales o gestionar upload físico en este módulo. Se descarta porque acopla el dominio a infraestructura de archivos y CHANGES define explícitamente referencia al almacenamiento.

### 2. Contexto académico validado por FKs existentes

Los servicios validan que `materia_id`, `carrera_id` y `cohorte_id` existan y pertenezcan al tenant autenticado. Para `FechaAcademica`, la asociación requerida es materia × cohorte; para `ProgramaMateria`, materia × carrera × cohorte.

Alternativa considerada: aceptar IDs opacos sin validar. Se descarta porque rompería integridad y permitiría referencias cross-tenant.

### 3. Listados separados para tabla y calendario sobre el mismo repositorio

El repositorio proveerá filtros por contexto (`materia_id`, `carrera_id`, `cohorte_id`, `tipo`, `periodo`, rango de fechas) y el service expondrá respuestas tabulares o calendario sin duplicar queries en routers.

Alternativa considerada: endpoints totalmente separados con lógica duplicada. Se descarta para mantener queries solo en repositories y lógica de presentación en services/schemas.

### 4. Fragmento LMS generado como salida determinística

La generación para LMS se implementará como función/service puro que transforma fechas académicas ordenadas en HTML/texto simple estable, sin side effects ni integración externa.

Alternativa considerada: worker o integración Moodle automática. Se descarta por fuera de alcance de C-17.

### 5. Unicidad funcional por contexto

`FechaAcademica` debe evitar duplicados para `(tenant_id, materia_id, cohorte_id, tipo, numero, periodo)` mientras no esté soft-deleted. `ProgramaMateria` debe evitar duplicados activos para `(tenant_id, materia_id, carrera_id, cohorte_id, titulo)` o definir reemplazo explícito vía update.

Alternativa considerada: permitir duplicados libres. Se descarta porque dificulta calendario y fuente única de documentos vigentes.

## Risks / Trade-offs

- [Referencia opaca inválida] El backend no sabe si el archivo existe realmente → Mitigación: validar presencia/formato básico y dejar verificación del storage a la capa que emite la referencia.
- [Duplicados con soft delete] Constraints parciales pueden variar por motor → Mitigación: usar índices/constraints PostgreSQL adecuados y tests de unicidad con DB real.
- [HTML LMS demasiado específico] Moodle puede requerir formato distinto por tenant → Mitigación: generar fragmento simple y estable, fácil de reemplazar en un change futuro.
- [Permiso amplio] `estructura:gestionar` cubre ambas operaciones → Mitigación: fail-closed con guard en todos los endpoints y tenant desde JWT.

## Migration Plan

1. Crear migración Alembic dedicada para `programa_materia` y `fecha_academica` con FKs a estructura académica, `tenant_id`, soft delete e índices por filtros frecuentes.
2. Implementar modelos SQLAlchemy y repositories tenant-scoped.
3. Implementar services, schemas y routers para programas y fechas académicas.
4. Agregar tests TDD para persistencia, servicios y API con PostgreSQL real/efímero.
5. Rollback: eliminar tablas/índices de C-17; en producción respaldar referencias documentales antes de downgrade.

## Open Questions

- ¿El formato del fragmento LMS debe ser HTML puro, Markdown o ambos? Para C-17 se asume HTML simple y respuesta textual estable.
- ¿Debe existir un solo programa vigente por materia×carrera×cohorte o múltiples versiones por título? Para C-17 se asume evitar duplicados activos por título y permitir historial vía soft delete.
