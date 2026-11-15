# API guide

Swagger UI is available at `/docs`; OpenAPI JSON is at `/openapi.json`.

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/health` | No | Liveness |
| POST | `/api/v1/auth/register` | No | Create tenant and owner |
| POST | `/api/v1/auth/login` | No | Obtain access token |
| GET | `/api/v1/auth/me` | Yes | Current identity and tenant |
| POST | `/api/v1/products` | Owner/admin/inventory manager | Create SKU |
| GET | `/api/v1/products` | Yes | Tenant product list |
| POST | `/api/v1/suppliers` | Yes | Create supplier |
| POST | `/api/v1/customers` | Yes | Create customer |
| POST | `/api/v1/warehouses` | Yes | Create warehouse |
| POST | `/api/v1/inventory/adjustments` | Owner/admin/inventory/warehouse manager | Ledger-backed adjustment |
| GET | `/api/v1/inventory/balances` | Yes | Inventory projection |
| GET | `/api/v1/inventory/movements` | Yes | Movement history |

Example registration:

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"organization_name":"Acme Tools","full_name":"Asha Owner","email":"asha@example.com","password":"ChangeThisPass123!"}'
```

Pass the returned `access_token` as `Authorization: Bearer <token>`. All protected business queries scope to the membership's organization.
