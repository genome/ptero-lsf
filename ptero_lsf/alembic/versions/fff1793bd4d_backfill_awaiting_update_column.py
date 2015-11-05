"""backfill_awaiting_update_column

Revision ID: fff1793bd4d
Revises: 14ef3ba450df
Create Date: 2015-11-05 02:06:27.875497

"""

# revision identifiers, used by Alembic.
revision = 'fff1793bd4d'
down_revision = '14ef3ba450df'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute("UPDATE job SET awaiting_update = FALSE WHERE awaiting_update IS NULL")


def downgrade():
    pass

# flake8: noqa
