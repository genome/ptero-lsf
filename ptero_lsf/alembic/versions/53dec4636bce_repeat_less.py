"""repeat_less

Revision ID: 53dec4636bce
Revises: 1bd189b92003
Revises: 14ef3ba450df
Create Date: 2015-11-04 06:19:23.850932

"""

# revision identifiers, used by Alembic.
revision = '53dec4636bce'
down_revision = '14ef3ba450df'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('job_status_history', sa.Column('last_updated', sa.DateTime(timezone=True), nullable=True))
    op.add_column('job_status_history', sa.Column('times_seen', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('job_status_history', 'times_seen')
    op.drop_column('job_status_history', 'last_updated')

# flake8:noqa
