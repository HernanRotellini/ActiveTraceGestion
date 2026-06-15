## Context

El backend usa endpoints paginados que devuelven `{ items: T[] | null, total: number }`. Cuando no hay datos (consulta post-RBAC con permisos restringidos o datos semilla no cargados), algunos endpoints retornan `items: null` en vez de `items: []`. El frontend itera con `data?.items.map(...)`, que falla si `items` es null/undefined porque `?.` solo cubre `data`, no `items`.

## Goals / Non-Goals

**Goals:**
- Eliminar todos los crashes `Cannot read properties of undefined/null (reading 'map')` en pantallas que iteran listas paginadas
- Aplicar el fix más mínimo posible: solo agregar `?.` antes de `.map()`

**Non-Goals:**
- No cambiar el tipado de la API (el backend podría corregir `null`→`[]` después, pero el frontend debe ser tolerante)
- No refactorizar componentes ni modificar lógica
- No tocar componentes que ya usan `data?.items?.map(...)` o `?? []`

## Decisions

| Decisión | Opciones | Elegida | Razón |
|----------|----------|---------|-------|
| Patrón de seguridad | `?.map` vs `?? [].map` vs early return | `?.items?.map()` | Mínimo cambio, misma línea, no afecta el empty-state existente (ya hay `(!data?.items || data.items.length === 0)` checks) |
| Cobertura | Solo 13 archivos vs todos los .map() | 13 archivos | Los demás ya son seguros (guard checks, `?? []`, o `?.map`) |

## Risks / Trade-offs

- [Bajo] `?.items?.map()` retorna `undefined` si items es null → la expresión JSX simplemente no renderiza nada. Ya existen guards de empty state en todos los componentes, así que es seguro.
- [Bajo] Si el backend eventualmente nunca retorna `null`, los `?.` son ruido sintáctico. Costo ~13 caracteres por archivo.
