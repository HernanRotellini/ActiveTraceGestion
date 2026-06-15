## Context

The sidebar in `frontend/src/layouts/MainLayout.tsx` currently renders 22 menu items as a flat `<ul>` list with no categorization. Items related to education, billing, and audit are interleaved arbitrarily. The `MenuItem` interface has `{ label, route, requiredPermission? }` with no grouping concept. The component filters items by permissions and maps them into `<NavLink>` elements.

This change introduces visual categorization without altering any routing, permissions, or business logic — pure presentation.

## Goals / Non-Goals

**Goals:**
- Group sidebar items into 3 logical categories: EDUCATIVO, FACTURACIÓN Y SALARIOS, AUDITORÍA
- Add a `group` field to `MenuItem` to declare each item's category
- Render section headers (category titles) as visual separators
- Keep "Inicio" as a standalone item at the top
- Maintain responsive behavior (mobile drawer, desktop static)

**Non-Goals:**
- No changes to the routing system or routes
- No changes to permission/authorization logic
- No backend changes
- No new icons or visual assets (section headers are text-only)
- No drag-to-reorder or user-customizable sidebar

## Decisions

### 1. Group type as string union instead of enum
Use a TypeScript string union type (`'educativo' | 'facturacion' | 'auditoria' | undefined`) rather than a runtime enum. This keeps the code simpler and avoids importing an enum constant. The `undefined` value is reserved for "Inicio" (standalone, no category).

### 2. Section headers rendered as `<li>` headings
Section headers will be rendered as non-interactive `<li>` elements with uppercase text and a bottom border or top spacing to visually separate groups. This keeps the existing `<ul>` structure intact and avoids nesting `<ul>` elements.

### 3. Ordered array definition with items contiguous by group
Items within each group are contiguous in the `menuItems` array. The array follows the order: Inicio → EDUCATIVO items → FACTURACIÓN Y SALARIOS items → AUDITORÍA items. This makes the source order the visual order without needing sorting logic.

### 4. Filtering per-item (unchanged)
Permission filtering continues per-item as before — no group-level permissions. Each item retains its `requiredPermission`; if a user cannot see any item in a group, the group header will still render above zero visible items. This is acceptable because groups are logical categories, and hiding the header would create visual confusion when permissions change dynamically.

## Risks / Trade-offs

- **[Low] Empty group renders header**: If all items in a category are hidden by permissions, the header still renders. Mitigation: accept this as minor visual noise, or filter headers post-hoc by checking if any visible item belongs to the group.
- **[Low] Hardcoded order**: Adding a new item means inserting it in the right position. Mitigation: the `group` field makes it explicit; developers just need to place it among siblings of the same group.
