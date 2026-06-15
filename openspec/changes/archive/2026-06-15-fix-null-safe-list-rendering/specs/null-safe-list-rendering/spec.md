## ADDED Requirements

### Requirement: Frontend SHALL tolerate `items: null` from paginated API responses

All paginated API endpoints return `{ items: T[] | null, total: number }`. When `items` is `null` or `undefined`, the frontend SHALL NOT crash and SHALL render the empty state instead.

#### Scenario: Page renders with null items from API
- **WHEN** a paginated endpoint returns `{ items: null, total: 0 }`
- **THEN** the frontend SHALL render the empty-state message ("No hay X registradas.") without crashing

#### Scenario: Page renders with empty array from API  
- **WHEN** a paginated endpoint returns `{ items: [], total: 0 }`
- **THEN** the frontend SHALL render the empty-state message (existing behavior preserved)

#### Scenario: Items are available
- **WHEN** a paginated endpoint returns `{ items: [...], total: N }`
- **THEN** the frontend SHALL render the list (existing behavior preserved)
