# Project Structure

StockFlow ERP is organized as a modular monolith. The application is deployed as one
service while keeping infrastructure, API routing, and business-domain code separated.

```text
StockFlow-ERP/
├── .github/workflows/   # Continuous integration workflows
├── app/
│   ├── core/            # Settings, database setup, security, dependencies
│   ├── api/v1/          # Versioned HTTP API routes
│   └── modules/         # Business-domain modules
│       ├── identity/    # Organization and user identity functionality
│       ├── catalog/     # Product, supplier, customer, warehouse and related models
│       └── inventory/   # Inventory business services
├── migrations/          # Alembic migration environment and revisions
├── scripts/             # Developer and administration scripts
├── tests/                # Automated tests
├── docs/                 # Architecture, API, security and operational documentation
├── powerbi/              # Reporting SQL and DAX measures
├── Dockerfile            # Container image definition
├── docker-compose.yml    # Local service orchestration
├── alembic.ini           # Alembic configuration
└── pyproject.toml        # Python package metadata and tool configuration
```

## Design notes

- `app/core` contains cross-cutting infrastructure and should not contain domain workflows.
- `app/api/v1` translates HTTP requests into calls to application/domain services.
- `app/modules` groups business logic by domain. Keep domain rules out of route handlers.
- `migrations` is the source of truth for schema changes; do not edit the database manually
  as a substitute for a migration.
- `tests` should cover successful workflows, validation failures, authorization boundaries,
  and important inventory consistency rules.
- `powerbi` contains reporting assets and is separate from runtime API code.

Only create additional domain modules or route packages when there is implemented code to put
in them; avoid empty folders added only to make the tree look larger.
