## Requirements

### Requirement: Tenant root entity
The system SHALL provide a `Tenant` root entity that represents an institution and can be referenced by all future tenant-scoped domain entities.

#### Scenario: Tenant can be persisted
- **WHEN** a tenant is created with valid required attributes
- **THEN** the system persists it with an internal UUID and timestamps

#### Scenario: Tenant is not self-scoped
- **WHEN** the Tenant model is inspected
- **THEN** it does not require a `tenant_id` pointing to another tenant

### Requirement: Tenant-scoped entity base
The system SHALL provide a reusable base/mixin for tenant-scoped entities with UUID `id`, `tenant_id`, `created_at`, `updated_at`, and nullable `deleted_at` fields.

#### Scenario: New tenant-scoped record gets base fields
- **WHEN** a tenant-scoped record is persisted
- **THEN** it has an internal UUID, the assigned `tenant_id`, `created_at`, `updated_at`, and no `deleted_at`

#### Scenario: Timestamp updates on modification
- **WHEN** a tenant-scoped record is modified and saved
- **THEN** `updated_at` changes while `created_at` remains stable

### Requirement: Repository tenant scope by default
Tenant-scoped repositories SHALL require a tenant context and SHALL filter every normal read/write operation by that tenant by default.

#### Scenario: Tenant cannot read another tenant record
- **WHEN** tenant A and tenant B both have records in the same table
- **THEN** a repository scoped to tenant A returns only tenant A records

#### Scenario: Cross-tenant get returns not found
- **WHEN** a repository scoped to tenant A requests a record id that belongs to tenant B
- **THEN** the system treats it as not found

#### Scenario: Repository without tenant context fails closed
- **WHEN** a tenant-scoped repository is created or used without a tenant id
- **THEN** the system rejects the operation instead of performing an unscoped query

### Requirement: Soft delete is the default deletion behavior
The system SHALL soft-delete tenant-scoped records by setting `deleted_at` and SHALL exclude soft-deleted records from normal repository reads.

#### Scenario: Delete marks record as deleted
- **WHEN** a tenant-scoped record is deleted through its repository
- **THEN** the record remains in the database with `deleted_at` populated

#### Scenario: Soft-deleted record is hidden by default
- **WHEN** a normal repository list or get operation is performed after soft delete
- **THEN** the soft-deleted record is not returned

#### Scenario: Hard delete is not used for domain deletion
- **WHEN** domain code requests deletion of a tenant-scoped record
- **THEN** the repository performs a soft delete rather than physically removing the row

### Requirement: Alembic migration for tenant foundation
The system SHALL include an Alembic migration that creates the tenant foundation schema needed by this change.

#### Scenario: Migration creates tenant table
- **WHEN** migrations are applied to an empty test database
- **THEN** the tenant table exists with UUID primary key and lifecycle columns

#### Scenario: Migration rollback is scoped
- **WHEN** the tenant migration is rolled back
- **THEN** only schema introduced by this change is removed
