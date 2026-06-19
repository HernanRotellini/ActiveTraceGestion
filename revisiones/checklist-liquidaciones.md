# Checklist — Liquidaciones / Facturación

> Fuentes: `backend/app/api/v1/routers/liquidaciones.py`, `backend/app/api/v1/routers/facturas.py`, `backend/app/schemas/liquidaciones.py`, `backend/app/models/liquidaciones.py`

## Contratos de API (según backend)

### Grilla salarial
- [x] `POST /api/liquidaciones/grilla/bases` → `SalarioBaseResponse` (201)
- [x] `GET /api/liquidaciones/grilla/bases` → `SalarioBaseResponse[]`
- [x] `PUT /api/liquidaciones/grilla/bases/{id}` → `SalarioBaseResponse` (no PATCH)
- [x] `DELETE /api/liquidaciones/grilla/bases/{id}` → 204
- [x] `POST /api/liquidaciones/grilla/pluses` → `SalarioPlusResponse` (201)
- [x] `GET /api/liquidaciones/grilla/pluses` → `SalarioPlusResponse[]`
- [x] `POST /api/liquidaciones/grilla/materia-plus` → `MateriaPlusResponse` (201)
- [x] `GET /api/liquidaciones/grilla/materia-plus` → `MateriaPlusResponse[]`

### Liquidaciones
- [x] `POST /api/liquidaciones/preview` → `LiquidacionPreviewResponse`
- [x] `POST /api/liquidaciones/cerrar` → `LiquidacionResponse[]` (201)
- [x] `GET /api/liquidaciones` → `LiquidacionResponse[]` (filtros: periodo, cohorte_id, usuario_id, segmento)
- [x] `GET /api/liquidaciones/{id}` → `LiquidacionResponse`

### Facturas
- [x] `POST /api/facturas` → `FacturaResponse` (201)
- [x] `GET /api/facturas` → `FacturaResponse[]` (filtros: usuario_id, periodo, estado, desde, hasta)
- [x] `GET /api/facturas/{id}` → `FacturaResponse`
- [x] `PUT /api/facturas/{id}` → `FacturaResponse` (no PATCH)
- [x] `DELETE /api/facturas/{id}` → 204
- [x] `POST /api/facturas/{id}/abonada` → `FacturaResponse`

## Tipos correctos

### Enums
- [x] `RolLiquidacion`: 'PROFESOR' | 'TUTOR' | 'NEXO' | 'COORDINADOR'
- [x] `EstadoLiquidacion`: 'Abierta' | 'Cerrada'
- [x] `EstadoFactura`: 'Pendiente' | 'Abonada'
- [x] `SegmentoLiquidacion`: 'general' | 'nexo' | 'facturante'

### SalarioBase
- [x] Eliminado campo `activo: boolean` (no existe en backend)
- [x] `monto` es string (Decimal serializado como string en JSON)
- [x] `desde`/`hasta` son strings de fecha (date)
- [x] `created_at` es string datetime

### Plus (SalarioPlus)
- [x] Renombrado de `Plus` a `SalarioPlusResponse`
- [x] Eliminado campo `activo: boolean`
- [x] `monto` es string (Decimal)
- [x] Payload requiere `rol: RolLiquidacion`

### Liquidacion
- [x] Eliminado `LiquidacionItem` (modelo ficticio — no existe)
- [x] `LiquidacionResponse` per-docente: id, cohorte_id, usuario_id, periodo, rol, estado, monto_base, monto_plus, monto_total, comisiones[], es_nexo, excluido_por_factura, created_at
- [x] `LiquidacionPreviewResponse`: cohorte_id, periodo, items[], total_pagable, segmento_nexo_total, segmento_facturantes_total
- [x] Filtros: periodo (YYYY-MM), cohorte_id, usuario_id, segmento (no `docente` ni `mes` ni `page`)

### Factura
- [x] Eliminado `docente_id`/`docente_nombre`/`importe`/`observaciones`/`creada_en`/`abonada_en`
- [x] `FacturaResponse`: id, usuario_id, periodo, detalle, referencia_archivo, archivo_size_bytes, estado, abonada_at?, created_at
- [x] `FacturaCreate`: usuario_id, periodo, detalle, referencia_archivo, archivo_size_bytes
- [x] Filtros: usuario_id, periodo, estado, desde, hasta (no `docente`, `q`, `page`)

## Servicio

- [x] Liquidaciones URL base: `/api/liquidaciones` (con `/api/` prefix)
- [x] Facturas URL base: `/api/facturas`
- [x] `cerrarLiquidacion` es `POST /api/liquidaciones/cerrar` con body `{cohorte_id, periodo}` (no `/{id}/cerrar`)
- [x] `actualizarSalarioBase` usa `PUT` (no `PATCH`)
- [x] `actualizarFactura` usa `PUT` (no `PATCH`)
- [x] `marcarFacturaAbonada` es `POST /api/facturas/{id}/abonada`

## Hooks

- [x] `useSalariosBase`, `useCrearSalarioBase`, `useActualizarSalarioBase`, `useEliminarSalarioBase`
- [x] `usePlus`, `useCrearPlus`
- [x] `useMateriaPlus`, `useCrearMateriaPlus`
- [x] `usePreviewLiquidacion`, `useCerrarLiquidacion`
- [x] `useLiquidaciones`, `useLiquidacion`
- [x] `useFacturas`, `useCrearFactura`, `useActualizarFactura`, `useEliminarFactura`, `useMarcarAbonada`

## Páginas / Componentes

### GrillaSalarialPage
- [x] Lista salarios base y pluses reales desde API
- [x] Formulario crea salario base con rol (enum select), monto, desde, hasta
- [x] Formulario crea plus con rol, grupo, descripcion, monto, desde, hasta
- [x] Eliminar salario base via DELETE

### LiquidacionPeriodoPage (preview + cerrar)
- [x] Preview: form con cohorte_id + periodo → muestra items del preview
- [x] KPIs: total_pagable, segmento_nexo_total, segmento_facturantes_total
- [x] Cerrar: `POST /api/liquidaciones/cerrar` con body correcto
- [x] Tabla de items con usuario_id, rol, monto_base, monto_plus, monto_total, procesable

### LiquidacionHistorialPage
- [x] Lista `LiquidacionResponse[]` reales
- [x] Filtros: periodo, cohorte_id, segmento
- [x] Tabla con columnas correctas del backend

### FacturasPage
- [x] Lista `FacturaResponse[]` reales
- [x] Filtros: periodo, estado, desde, hasta (sin `docente`, `page`)
- [x] Crear factura con usuario_id, periodo, detalle, referencia_archivo, archivo_size_bytes
- [x] Marcar abonada via `POST /api/facturas/{id}/abonada`
- [x] Eliminar via DELETE

## Tests

- [x] `Liquidaciones.test.tsx` actualizado con tipos correctos del backend

## Criterios transversales

- [x] URLs con `/api/` prefix
- [x] Identidad desde JWT
- [x] RBAC: `liquidaciones:ver`, `liquidaciones:gestionar`, `liquidaciones:operar_grilla`, `facturas:gestionar`
- [x] Sin `any` en TypeScript
- [x] Soft delete (DELETE via backend service)
