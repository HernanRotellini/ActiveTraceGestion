## Why

The sidebar navigation presents 22 tools in a flat, unordered list with no visual grouping or section headers. As the platform grows, users struggle to find tools quickly — academic, financial, and audit items are mixed together with no logical structure. This creates friction and increases cognitive load, especially for power users who navigate between multiple tools daily.

## What Changes

- Add a `group` field to the `MenuItem` interface to categorize each item into a logical section
- Define 3 visual categories with section headers: **EDUCATIVO**, **FACTURACIÓN Y SALARIOS**, **AUDITORÍA**
- Render the sidebar as grouped sections with visual separators between categories
- Keep "Inicio" as a standalone item at the very top, outside any category
- The ordering within each category preserves the existing relative order
- No changes to routing, permissions, or business logic — purely a frontend presentation change

## Capabilities

### New Capabilities
- `sidebar-categories`: Categorize sidebar navigation items into logical groups with section headers and visual separation. This capability covers the grouping structure, the rendering logic, and the visual design of the categorized sidebar.

### Modified Capabilities
*(None — this change does not alter requirements, only presentation.)*

## Impact

- **File modified**: `frontend/src/layouts/MainLayout.tsx` — Update `MenuItem` interface, reorganize `menuItems` array with group assignments, add section header rendering logic
- **File possibly updated**: `frontend/src/test/SidebarPermissions.test.tsx` — Verify tests still pass after restructuring
- **No new dependencies** — Pure frontend change using existing React, Tailwind CSS patterns
- **No API changes** — No backend, database, or schema changes
