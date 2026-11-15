"""Alembic environment; imports model modules so metadata is complete."""
from alembic import context
from sqlalchemy import engine_from_config, pool
from app.core.config import get_settings
from app.core.database import Base
from app.modules.identity import models as identity_models
from app.modules.catalog import models as catalog_models
config = context.config
target_metadata = Base.metadata

def run_migrations_offline():
    context.configure(url=get_settings().database_url, target_metadata=target_metadata,
                      literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction(): context.run_migrations()

def run_migrations_online():
    section = config.get_section(config.config_ini_section) or {}
    section["sqlalchemy.url"] = get_settings().database_url
    connectable = engine_from_config(section, prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction(): context.run_migrations()

if context.is_offline_mode(): run_migrations_offline()
else: run_migrations_online()
