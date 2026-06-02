## Context

El proyecto activia-trace requiere un sistema de autorización basado en RBAC con permisos finos (`modulo:accion`). Actualmente C-03 autentica usuarios y resuelve sus roles en `CurrentUser`, pero no hay un mecanismo que evalúe permisos por endpoint. El catálogo de roles y permisos debe ser administrable (datos en DB, no hardcode), extensible por tenant, y la matriz base debe sembrarse desde la especificación del dominio.

## Goals / Non-Goals

**Goals:**
- Modelar roles, permisos y asignación rol-permiso como tablas en DB (catálogo administrable)
- Sembrar la matriz base de 7 roles × ~20 permisos (03_actores_y_roles.md §3.3)
- Proveer un servicio de resolución de permisos efectivos por request (unión de roles del usuario, acotada por tenant)
- Implementar `require_permission("modulo:accion")` como FastAPI dependency que produce 403 si el permiso falta
- Migración 003 con tablas + seed

**Non-Goals:**
- Gestión de vigencia temporal de asignaciones (se hará en C-06 estructura académica)
- Interfaz CRUD administrable de roles/permisos (solo seed + modelo datos; UI en C-21)
- Impersonación (usa `impersonacion:usar` pero se implementa en change separado)
- Cacheo de permisos (resolución server-side en cada request, optimizable luego)

## Decisions

### D1: Rol y Permiso como tablas propias con tenant_id
Rol y Permiso heredan de `TenantScopedMixin`. Aunque la matriz base es igual para todos los tenants, tener `tenant_id` permite que cada institución personalice su catálogo (agregar roles propios, deshabilitar permisos). Alternativa considerada: tabla global compartida. Rechazada porque rompe el aislamiento multi-tenant: un tenant podría modificar permisos de otro.

### D2: RolPermiso como tabla de asignación con datos
La matriz rol × permiso se modela como tabla `rol_permiso` con FK a ambas tablas, más flags `habilitado` y `alcance` (global vs propio). `alcance = "global"` significa que el permiso aplica sobre cualquier recurso del módulo; `alcance = "propio"` significa que solo aplica sobre recursos propios del usuario, a ser validado por la lógica del endpoint. Este flag es informativo para el endpoint y no lo resuelve el guard.

Alternativa considerada: definir la matriz hardcodeada en código Python. Rechazada: la KB exige catálogo administrable como datos.

### D3: Permisos efectivos resueltos como intersect de roles en DB
En cada request, el guard `require_permission` obtiene los roles del `CurrentUser`, consulta `SELECT permiso.codigo FROM rol_permiso JOIN permiso WHERE rol IN (...) AND habilitado = true`, y compara contra el permiso requerido. Esto es una query liviana (un JOIN, filtrada por tenant y roles).

Alternativa considerada: embebir permisos en el JWT. Rechazada: los permisos pueden cambiar sin necesidad de re-login; la KB (03_actores_y_roles.md §3.2) dice "los permisos se resuelven server-side en cada petición, nunca se almacenan en el token".

### D4: `require_permission` como dependency parametrizada
Se implementa como `RequirePermission` clase callable que recibe el permiso en el constructor y usa `Depends(get_current_user)` internamente. Esto permite:
```python
@router.get("/calificaciones")
async def listar(_: CurrentUser = Depends(require_permission("calificaciones:importar"))):
    ...
```

Alternativa considerada: decorador de función. Rechazada: FastAPI no soporta decoradores con inyección de dependencias correctamente. Las dependencies son el patrón canónico.

### D5: Seed de la matriz base en migración 003 de Alembic
El seed se ejecuta como operación de migración, no como fixture ni script separado. Esto garantiza que al crear la base (dev, test, prod) la matriz esté presente. Se usa `op.execute` con inserts directos a las tablas usando los códigos de permiso definidos en la KB.

### D6: Evaluación del flag (propio) delegada al endpoint
El guard `require_permission` solo verifica posesión del permiso (booleano). El alcance `(propio)` es una convención semántica del permiso (ej. `calificaciones:importar_propio` vs `calificaciones:importar`) que el endpoint debe validar contra el contexto del recurso. Alternativa: el guard evalúa alcance. Rechazada porque el guard no tiene acceso al recurso siendo accedido.

## Risks / Trade-offs

- [Riesgo] Consulta DB por request en cada endpoint protegido: 1-2ms por query, aceptable para el volumen esperado. Si escala, migrar a Redis con invalidación por cambio de roles.
- [Riesgo] Permisos codificados como strings literales en decoradores: propenso a typos. Mitigación: definir constantes `Permiso.CALIFICACIONES_IMPORTAR = "calificaciones:importar"` en el modelo.
- [Trade-off] Seed en migración: no se puede modificar la matriz base sin una nueva migración. Esto es deliberado: los cambios seed son cambios de esquema/dominio que deben versionarse.
- [Riesgo] El flag `alcance` (propio/global) es informativo y no tiene enforcement automático. El equipo debe acordar la convención antes de implementar endpoints.
