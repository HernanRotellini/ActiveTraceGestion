## ADDED Requirements

### Requirement: Sidebar items are grouped into logical categories
The sidebar SHALL organize navigation items into 3 categories: EDUCATIVO, FACTURACIÓN Y SALARIOS, AUDITORÍA. Each category SHALL have a visual section header. "Inicio" SHALL remain standalone at the top without a category header.

#### Scenario: EDUCATIVO category contains academic tools
- **WHEN** the sidebar renders
- **THEN** items (Carreras, Cohortes, Materias, Setup cuatrimestre, Mis Comisiones, Entregas sin corregir, Comunicaciones, Monitor, Equipos docentes, Avisos, Tareas internas, Encuentros, Coloquios, Monitor general, Usuarios) SHALL appear under a section header labeled "EDUCATIVO"

#### Scenario: FACTURACIÓN Y SALARIOS category contains financial tools
- **WHEN** the sidebar renders
- **THEN** items (Liquidaciones, Grilla salarial, Facturas) SHALL appear under a section header labeled "FACTURACIÓN Y SALARIOS"

#### Scenario: AUDITORÍA category contains audit tools
- **WHEN** the sidebar renders
- **THEN** items (Auditoría, Log auditoría) SHALL appear under a section header labeled "AUDITORÍA"

#### Scenario: Inicio remains standalone at top
- **WHEN** the sidebar renders
- **THEN** "Inicio" SHALL appear as the first item, separated from category groups below

### Requirement: MenuItem interface includes a group field
The `MenuItem` interface SHALL support an optional `group` field of type `'educativo' | 'facturacion' | 'auditoria'`.

#### Scenario: Menu items declare their category
- **WHEN** a menu item is defined
- **THEN** it MAY include a `group` field indicating its category
- **AND** items without a `group` field (like "Inicio") SHALL render standalone

### Requirement: Section headers render as visual separators
Each category group SHALL display a section header with uppercase text and visual styling that distinguishes it from navigation links.

#### Scenario: Section header is not clickable
- **WHEN** a section header is rendered
- **THEN** it SHALL NOT be a clickable navigation link
- **AND** it SHALL be visually distinct from menu items (e.g., uppercase, smaller font, muted color, top border/margin)

### Requirement: Permission filtering continues per-item
Permission-based visibility SHALL continue to be evaluated per individual menu item, not per group.

#### Scenario: Items hidden by permission are not rendered
- **WHEN** a user lacks the required permission for a menu item
- **THEN** that item SHALL NOT be rendered in the sidebar
- **AND** other items in the same group SHALL still render normally if permitted
