## 1. Helper `wrap_list` para responses

- [x] 1.1 Crear función `wrap_list(items)` en `estructura_academica.py` que devuelve `{"items": items, "total": len(items)}`
- [x] 1.2 Aplicar `wrap_list()` a `GET /api/admin/carreras`, `GET /api/admin/cohortes`, `GET /api/admin/materias`

## 2. Normalizar campos en schemas Pydantic

- [x] 2.1 Agregar `activo: bool = computed_field` y `creada_en: datetime = computed_field` a `CarreraResponse`
- [x] 2.2 Agregar `activo: bool = computed_field` y `creada_en: datetime = computed_field` a `CohorteResponse`
- [x] 2.3 Agregar `activo: bool = computed_field` y `creada_en: datetime = computed_field` a `MateriaResponse`
- [x] 2.4 Agregar `descripcion: str = ""` a `CarreraResponse`
- [x] 2.5 Agregar `carrera_id: UUID | None`, `cohorte_id: UUID | None`, `carga_horaria: int = 0`, `carrera_nombre: str | None = None`, `cohorte_nombre: str | None = None` a `MateriaResponse`
- [x] 2.6 Actualizar `CarreraUpdate` para aceptar `codigo` como campo opcional

## 3. Agregar PATCH cohortes

- [x] 3.1 Crear schema `CohorteUpdate` en schemas con `nombre`, `anio`, `vig_desde`, `vig_hasta` opcionales
- [x] 3.2 Agregar método `update_cohorte()` en `EstructuraAcademicaService`
- [x] 3.3 Agregar endpoint `PATCH /api/admin/cohortes/{cohorte_id}` en el router

## 4. Filtros en listar materias

- [x] 4.1 Agregar query params `carrera_id: UUID | None` y `cohorte_id: UUID | None` a `GET /api/admin/materias`
- [x] 4.2 Modificar `list_materias()` en el service para aceptar filtros y hacer join con carreras/cohortes
- [x] 4.3 Modificar `list_materias()` en el service para devolver `carrera_nombre` y `cohorte_nombre`

## 5. Actualizar seed_dev_data

- [x] 5.1 Agregar `carga_horaria` y relaciones carrera/cohorte a las materias del seed
- [x] 5.2 Agregar `descripcion` a las carreras del seed

## 6. Tests

- [x] 6.1 Ejecutar tests existentes y verificar baseline
- [x] 6.2 Actualizar tests existentes para nuevo formato `{ items, total }`
- [x] 6.3 Agregar tests para nuevos campos computados (`activo`, `creada_en`)
- [x] 6.4 Verificar que todas las suites pasan (29 suites, 79+ tests)
