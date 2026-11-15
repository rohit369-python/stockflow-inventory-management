"""Initial schema migration. Metadata-driven creation keeps model and schema aligned."""
from alembic import op
from app.core.database import Base
from app.modules.identity import models as identity_models
from app.modules.catalog import models as catalog_models
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Create all initial application tables and constraints."""
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)

def downgrade():
    """Drop initial tables in dependency-aware reverse order."""
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
