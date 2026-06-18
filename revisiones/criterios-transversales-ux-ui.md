# Criterios transversales UX/UI

Estos criterios aplican a todas las pantallas del sistema. Cada pantalla debe revisarlos al momento de su checklist funcional.

## Mensajes y feedback

- [ ] No usar `alert`, `confirm` ni prompts nativos del navegador.
- [x] Usar toasts personalizados para errores.
- [x] Los toasts de error deben cerrarse automaticamente despues de 5 segundos.
- [x] Los toasts deben poder cerrarse manualmente.
- [ ] Los mensajes de error deben ser claros, accionables y orientados al usuario.
- [ ] No mostrar errores genericos cuando el backend o frontend conoce la causa.
- [x] Agregar toasts de exito para acciones completadas.
- [x] Los toasts de exito deben aplicarse de forma consistente en altas, ediciones, bajas, activaciones y desactivaciones.

Estado:
- Carreras, Cohortes y Materias usan el componente compartido `Toast`.
- Los toasts de error y exito se cierran automaticamente a los 5 segundos y pueden cerrarse manualmente.
- Las siguientes pantallas deben reutilizar `frontend/src/shared/components/Toast.tsx` en lugar de crear variantes locales.

## Confirmaciones

- [ ] Las acciones destructivas o sensibles deben usar modales propios de confirmacion.
- [ ] El modal debe explicar que entidad se esta afectando.
- [ ] El modal debe explicar la consecuencia de la accion.
- [ ] El boton principal de una accion destructiva debe usar estilo de peligro.
- [ ] El usuario siempre debe poder cancelar sin efectos secundarios.

## Acciones

- [ ] Acciones frecuentes de tabla deben usar iconos reconocibles.
- [ ] Editar debe usar icono de lapiz.
- [ ] Eliminar debe usar icono de tacho.
- [ ] Los iconos deben tener tooltips breves.
- [ ] Los iconos deben tener tamano suficiente para ser reconocibles.
- [ ] Los botones deben tener `aria-label` cuando solo muestran icono.

## Estados

- [ ] Estados binarios deben editarse con toggle, no con selector.
- [ ] El estado actual debe verse claramente en listados y formularios.
- [ ] Los cambios de estado deben mostrar feedback claro si fallan.
- [ ] Si una accion esta bloqueada por estado o dependencias, el mensaje debe explicar el motivo.

## Auditoria

- [ ] Toda accion significativa debe auditarse segun RN-23.
- [ ] Altas, ediciones, bajas, activaciones y desactivaciones deben generar registro de auditoria cuando afectan datos del dominio.
- [ ] Los cambios de estado deben auditar estado anterior y estado nuevo.
- [ ] La auditoria debe incluir identificador de la entidad afectada y datos minimos para reconocerla.
- [ ] No registrar auditoria si el usuario envia una edicion que no cambia el dato auditado.

## Consistencia visual

- [ ] No implementar funcionalidades que no esten pedidas por documentos o decision explicita de producto.
- [ ] Si una funcionalidad parece util pero no esta pedida, no se deja como pendiente funcional; solo se documenta como observacion si ayuda a evitar confusion.
- [x] Mantener un patron comun de filtros, tablas, acciones, modales y toasts.
- [ ] Evitar mezclar patrones distintos entre pantallas del mismo modulo.
- [ ] Mantener consistencia visual entre Carreras, Cohortes y Materias.
- [ ] Al detectar un nuevo criterio reusable, agregarlo en este documento y aplicarlo al revisar la siguiente pantalla.
