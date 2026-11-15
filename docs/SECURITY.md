# Security notes

- Passwords are hashed with Argon2id via `argon2-cffi`; raw passwords are never persisted.
- Access tokens are signed JWTs with short expiry and explicit token type.
- Tenant context is resolved from a verified token and active membership, not a request body organization ID.
- Role checks run on the API server.
- SQLAlchemy parameterization protects ordinary ORM queries from SQL injection.
- Stock adjustment requests require a reason and idempotency key.
- Do not expose `.env`; replace the development JWT secret before deployment.

Not yet implemented: refresh-token rotation/revocation, email verification/reset, login throttling, rate limiting, CSP/security headers, file-upload controls, PostgreSQL RLS and comprehensive permission matrix. Use HTTPS and a managed secret store in production. A production security review is required before real business data is used.
