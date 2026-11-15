# Contributing

- Use Python 3.13 and install `pip install -e '.[dev]'`.
- Keep HTTP routing thin; place business decisions in module services.
- Every tenant-owned query must include organization scope.
- Inventory changes must use the centralized inventory service and create a movement record.
- Add tests for business invariants and authorization boundaries.
- Run `python -m compileall -q app migrations scripts` and `pytest` before submitting changes.
- Generate and review Alembic migrations; do not edit deployed schemas manually.
