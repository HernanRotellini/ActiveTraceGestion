## Why

El change `C-18 liquidaciones-y-honorarios` está bloqueado por preguntas abiertas de prioridad alta sobre el cálculo de Plus salarial (`PA-22`, `PA-23`) y por dudas relacionadas con facturación (`PA-24`) y modalidad de cobro (`PA-17`). Sin cerrar estas reglas no es seguro implementar el cálculo de liquidaciones, porque el resultado contable podría ser incorrecto.

## What Changes

- Define un contrato funcional previo para liquidaciones: claves de Plus, mapeo Materia → clave, acumulación por comisiones, vigencia y alcance tenant.
- Cierra la semántica de cálculo del Plus cuando un docente tiene múltiples comisiones de la misma clave.
- Define cómo se modela la configuración de claves de Plus para que C-18 pueda implementarse sin hardcodear reglas institucionales.
- Documenta la relación mínima entre docentes facturantes, liquidación general y facturas para que C-18 no mezcle flujos contables.
- No implementa todavía endpoints ni modelos finales de liquidación; prepara las decisiones y criterios de aceptación necesarios para C-18.

## Capabilities

### New Capabilities
- `liquidaciones-reglas-salariales`: Reglas cerradas para grilla salarial, claves de Plus, mapeo de materias, acumulación por comisión y separación contable factura/liquidación.

### Modified Capabilities

No se modifican capacidades existentes; se introduce una capacidad contractual previa para desbloquear C-18.

## Impact

- OpenSpec: nueva spec `liquidaciones-reglas-salariales` que C-18 deberá leer antes de implementar.
- Knowledge base: requiere actualizar `knowledge-base/05_reglas_de_negocio.md`, `knowledge-base/04_modelo_de_datos.md`, `knowledge-base/06_funcionalidades.md` y retirar o marcar resueltas `PA-22`, `PA-23` — y, si se confirma, `PA-17`/`PA-24`.
- Backend futuro: C-18 deberá usar estas decisiones para modelos `SalarioBase`, `SalarioPlus`, `Liquidacion`, `Factura` y servicios de cálculo.
- Governance: CRÍTICO por afectar pagos/liquidaciones; este change es de decisión/especificación, no de código productivo.
