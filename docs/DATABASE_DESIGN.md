# Database design

Core relationships:

```mermaid
erDiagram
 ORGANIZATIONS ||--o{ MEMBERSHIPS : contains
 USERS ||--o{ MEMBERSHIPS : joins
 ORGANIZATIONS ||--o{ PRODUCTS : owns
 ORGANIZATIONS ||--o{ WAREHOUSES : owns
 ORGANIZATIONS ||--o{ SUPPLIERS : owns
 ORGANIZATIONS ||--o{ CUSTOMERS : owns
 WAREHOUSES ||--o{ INVENTORY_BALANCES : stores
 PRODUCTS ||--o{ INVENTORY_BALANCES : measured
 INVENTORY_BALANCES ||--o{ STOCK_MOVEMENTS : audited_by
 ORGANIZATIONS ||--o{ STOCK_MOVEMENTS : owns
```

All money uses `NUMERIC(14,2)`. Timestamps are timezone-aware at the model layer. Tenant and lookup columns are indexed. Product SKU and warehouse code are unique within an organization. Stock movement idempotency keys are unique within an organization.

The current ER diagram intentionally documents the implemented schema only; procurement, sales, payments, returns and dimensional BI tables are future migrations.
