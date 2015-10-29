"""awaiting_update

Revision ID: 3ea614162bd7
Revises: 1bd189b92003
Create Date: 2015-10-29 04:19:51.739591

"""

# revision identifiers, used by Alembic.
revision = '3ea614162bd7'
down_revision = '1bd189b92003'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('job', sa.Column('awaiting_update', sa.Boolean(), nullable=False))
    op.create_index(op.f('ix_job_awaiting_update'), 'job', ['awaiting_update'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_job_awaiting_update'), table_name='job')
    op.drop_column('job', 'awaiting_update')

# flake8: noqa
