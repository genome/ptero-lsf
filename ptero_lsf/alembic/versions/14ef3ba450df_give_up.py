"""give_up

Revision ID: 14ef3ba450df
Revises: 3ea614162bd7
Create Date: 2015-10-29 05:14:30.285605

"""

# revision identifiers, used by Alembic.
revision = '14ef3ba450df'
down_revision = '3ea614162bd7'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('job', sa.Column('failed_update_count', sa.Integer(), nullable=False))
    op.create_index(op.f('ix_job_failed_update_count'), 'job', ['failed_update_count'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_job_failed_update_count'), table_name='job')
    op.drop_column('job', 'failed_update_count')

# flake8: noqa
