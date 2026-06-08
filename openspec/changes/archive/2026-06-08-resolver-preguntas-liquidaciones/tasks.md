## 1. Validación de decisiones

- [x] 1.1 Revisar proposal, design y spec `liquidaciones-reglas-salariales` contra PA-22, PA-23, PA-17 y PA-24.
- [x] 1.2 Confirmar que las decisiones no requieren implementar código productivo en este change.
- [x] 1.3 Registrar que el dominio es CRÍTICO y que C-18 no debe empezar hasta archivar esta resolución.

## 2. Sincronización de base de conocimiento

- [x] 2.1 Actualizar `knowledge-base/05_reglas_de_negocio.md` para reflejar claves Plus configurables por tenant y acumulación por comisión activa.
- [x] 2.2 Actualizar `knowledge-base/04_modelo_de_datos.md` para incorporar el mapeo Materia→clave Plus con vigencia temporal y alcance por tenant.
- [x] 2.3 Actualizar `knowledge-base/06_funcionalidades.md` para aclarar administración de grilla salarial, Plus, facturantes y separación contable.
- [x] 2.4 Actualizar `knowledge-base/10_preguntas_abiertas.md` retirando o marcando resueltas PA-22 y PA-23; documentar decisión mínima para PA-17 y PA-24 si corresponde.

## 3. Preparación de C-18

- [x] 3.1 Actualizar `CHANGES.md` para indicar que C-18 depende de `resolver-preguntas-liquidaciones` ya archivado.
- [x] 3.2 Agregar en C-18 “Leer antes” la spec `openspec/specs/liquidaciones-reglas-salariales/spec.md` una vez archivada.
- [x] 3.3 Documentar criterios de aceptación que C-18 deberá testear: tenant isolation, acumulación por comisión, vigencia por período, facturantes fuera del total pagable.

## 4. Verificación

- [x] 4.1 Verificar que la spec tiene escenarios testeables con formato `#### Scenario`.
- [x] 4.2 Verificar que no quedan referencias contradictorias entre KB y spec sobre acumulación de Plus.
- [x] 4.3 Verificar que el change queda listo para archive y posterior propuesta de C-18.
