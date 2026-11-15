"""Create a first organization owner from environment variables for local setup."""
import os
from types import SimpleNamespace
from app.core.database import Base, engine, SessionLocal
from app.modules.identity.service import register

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    required = ["ORG_NAME", "ADMIN_NAME", "ADMIN_EMAIL", "ADMIN_PASSWORD"]
    missing = [key for key in required if not os.getenv(key)]
    if missing: raise SystemExit(f"Missing environment variables: {', '.join(missing)}")
    db = SessionLocal()
    try:
        result = register(db, SimpleNamespace(organization_name=os.environ["ORG_NAME"],
            full_name=os.environ["ADMIN_NAME"], email=os.environ["ADMIN_EMAIL"],
            password=os.environ["ADMIN_PASSWORD"]))
        print(f"Created owner for organization {result['organization_id']}")
    finally: db.close()
