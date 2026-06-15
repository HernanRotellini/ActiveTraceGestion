## 1. Update MenuItem Interface

- [x] 1.1 Add `group` field of type `'educativo' | 'facturacion' | 'auditoria' | undefined` to the `MenuItem` interface in `MainLayout.tsx`

## 2. Reorganize Menu Items with Group Assignments

- [x] 2.1 Assign `group: 'educativo'` to items: Carreras, Cohortes, Materias, Setup cuatrimestre, Mis Comisiones, Entregas sin corregir, Comunicaciones, Monitor, Equipos docentes, Avisos, Tareas internas, Encuentros, Coloquios, Monitor general, Usuarios
- [x] 2.2 Assign `group: 'facturacion'` to items: Liquidaciones, Grilla salarial, Facturas
- [x] 2.3 Assign `group: 'auditoria'` to items: Auditoría, Log auditoría
- [x] 2.4 Reorder the `menuItems` array: Inicio (no group) → EDUCATIVO group → FACTURACIÓN Y SALARIOS group → AUDITORÍA group, keeping items contiguous within their group

## 3. Render Section Headers in Sidebar

- [x] 3.1 Define a section header configuration (`{ label, group }`) for each category: EDUCATIVO, FACTURACIÓN Y SALARIOS, AUDITORÍA
- [x] 3.2 Update the sidebar rendering loop to detect group transitions and insert section header `<li>` elements before the first item of each group
- [x] 3.3 Style section headers: uppercase text, smaller font size (e.g., `text-xs`), muted text color (e.g., `text-gray-400`), with top margin/padding to visually separate groups
- [x] 3.4 Add top border or extra spacing between groups for clearer visual separation
- [x] 3.5 Update the `visibleItems` filtering to also track which groups have visible items — if a group has no visible items, skip rendering its section header

## 4. Verify Tests

- [x] 4.1 Run existing `SidebarPermissions` tests to confirm they pass with the restructured menu
- [x] 4.2 Verify the test still finds "Inicio" text in the rendered output

## 5. Visual Review

- [ ] 5.1 Build or dev-serve the frontend and verify the sidebar renders correctly with all 3 categories
- [ ] 5.2 Verify "Inicio" appears at the top as a standalone item
- [ ] 5.3 Verify responsive behavior (mobile drawer toggle) still works
- [ ] 5.4 Verify items hidden by permissions do not break the grouping layout
