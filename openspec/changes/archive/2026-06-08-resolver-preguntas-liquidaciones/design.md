## Context

El módulo `C-18 liquidaciones-y-honorarios` está marcado como CRÍTICO porque impacta pagos docentes. La KB ya define una fórmula general `Base + Σ(Plus)` y entidades conceptuales `SalarioBase`, `SalarioPlus`, `Liquidacion` y `Factura`, pero `PA-22` y `PA-23` seguían bloqueando el diseño implementable: faltaba definir cómo se configuran las claves de Plus, cómo se mapean a materias y cómo se acumulan cuando un docente tiene múltiples comisiones.

Este change no implementa el módulo de liquidaciones; establece las decisiones de producto y criterios de aceptación que deben sincronizarse en la KB antes de proponer/aplicar C-18.

## Goals / Non-Goals

**Goals:**
- Cerrar PA-22: definir que las claves de Plus son configurables por tenant y se asignan explícitamente a materias.
- Cerrar PA-23: definir que el Plus se acumula por cada comisión activa de una materia asignada a la clave durante el período liquidado.
- Dejar especificada la interacción mínima con facturación: modalidad de cobro determina si entra a liquidación general o flujo de facturas.
- Convertir estas decisiones en requisitos testeables para C-18.
- Actualizar la KB en apply, retirando o marcando resueltas las preguntas bloqueantes.

**Non-Goals:**
- No crear tablas/migraciones/product code de liquidaciones en este change.
- No definir importes reales de salarios o plus; son datos operativos configurables.
- No implementar conciliación bancaria ni integración con sistemas de pago.
- No implementar validación automática del monto de una factura contra una liquidación calculada equivalente.

## Decisions

### 1. Las claves de Plus son configurables por tenant

Cada tenant podrá definir su catálogo de claves de Plus (`PROG`, `BD`, `MAT`, etc.) y su descripción. No se hardcodean claves globales en el backend.

**Rationale:** las instituciones pueden tener familias de materias distintas; hardcodear el catálogo haría frágil el sistema y bloquearía onboarding de nuevos tenants.

**Alternativa considerada:** catálogo global fijo. Se descarta porque PA-22 pregunta explícitamente si el mapeo es configurable y el modelo multi-tenant requiere variación institucional.

### 2. El mapeo Plus se realiza por Materia dentro del tenant

Una materia puede tener cero o una clave de Plus vigente para un período determinado. Las materias sin clave asignada no generan Plus, pero sí pueden generar Base si corresponde al rol.

**Rationale:** `Materia` ya es la fuente única del catálogo académico; usarla como unidad de mapeo evita duplicar taxonomías.

**Alternativa considerada:** deducir clave desde `Materia.codigo` por prefijo (`PROG_*`). Se descarta porque introduce reglas implícitas no auditables.

### 3. El Plus se acumula por comisión activa

Si un docente tiene N comisiones activas de materias pertenecientes a la misma clave, el cálculo aplica `N × Plus(clave, rol)`. No hay tope por defecto. Si una institución necesita topes, será un change futuro explícito.

**Rationale:** RN-33/RN-34 ya expresan acumulación por `N_comisiones`; esta decisión cierra PA-23 y hace el cálculo determinístico.

**Alternativa considerada:** aplicar una sola vez por clave sin importar comisiones. Se descarta porque invisibiliza carga docente adicional.

### 4. La vigencia salarial se evalúa por período liquidado

`SalarioBase`, `SalarioPlus` y el mapeo Materia→clave tienen vigencia temporal. Para un período `AAAA-MM`, se usa la configuración vigente para ese mes.

**Rationale:** mantiene trazabilidad histórica y evita recalcular períodos cerrados con grillas nuevas.

### 5. La modalidad facturante excluye de la liquidación general

Un docente con modalidad de pago facturante no se incluye en el total pagable de la liquidación general Base+Plus. Puede mostrarse como segmento informativo y su cobro se gestiona por Factura.

**Rationale:** respeta RN-35/RN-38 y separa flujos contables.

### 6. Factura se asocia a docente y período, no a comisión

Para C-18, la factura será global por docente+período con detalle libre. No se valida automáticamente contra una liquidación equivalente porque el docente facturante queda fuera de Base+Plus pagable.

**Rationale:** cierra el mínimo necesario de PA-24 sin agregar conciliación compleja al MVP de C-18.

## Risks / Trade-offs

- [Configuración incompleta de claves] Una materia sin clave no genera Plus → Mitigación: C-18 debe exponer reportes/validaciones de materias sin clave antes de cerrar liquidación.
- [Cambios de mapeo a mitad de período] Puede afectar cálculo si no hay vigencia clara → Mitigación: vigencia por período y snapshot al cerrar liquidación.
- [Sin topes de acumulación] Puede generar montos altos si hay muchas comisiones → Mitigación: decisión explícita por ahora; topes quedan como change futuro si FINANZAS lo solicita.
- [Factura sin conciliación automática] Finanzas conserva control manual → Mitigación: facturas tienen estado y KPIs separados; conciliación avanzada queda fuera de alcance.

## Migration Plan

1. Actualizar KB con las decisiones cerradas: reglas RN-31/RN-34, entidades E17-E20 y funcionalidades F10.4-F10.6.
2. Retirar o marcar resueltas `PA-22`, `PA-23`; opcionalmente marcar resueltas `PA-17`, `PA-24` según el alcance aceptado.
3. Usar la spec `liquidaciones-reglas-salariales` como input obligatorio de C-18.
4. C-18 implementará modelos/migraciones/endpoints/tests a partir de estas reglas.

## Open Questions

- ¿FINANZAS quiere topes de acumulación por clave/rol? Para este diseño se asume que NO hay tope.
- ¿El mapeo Materia→clave necesita aprobación o auditoría explícita en UI? Para C-18 debe auditarse como cambio de grilla salarial.
