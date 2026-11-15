# Local deployment

1. Copy `.env.example` to `.env` and set a unique `JWT_SECRET_KEY` and database password.
2. Run `docker compose up --build -d`.
3. Run `docker compose exec api alembic upgrade head`.
4. Open `http://localhost:8000/docs`.

For local Python development, create a Python 3.13 virtual environment, run `pip install -e '.[dev]'`, set `DATABASE_URL` and `JWT_SECRET_KEY`, then `alembic upgrade head` and `uvicorn app.main:app --reload`.

Production deployment should use managed PostgreSQL, private Redis, TLS termination, non-root containers, secret manager injection, backups, monitoring, and a reviewed migration process. AWS ECS/Fargate or App Runner can host the API; RDS PostgreSQL and ElastiCache are suitable managed dependencies. This repository is not a turnkey AWS deployment.
