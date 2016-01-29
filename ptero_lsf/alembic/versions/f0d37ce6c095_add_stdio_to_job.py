"""Add stdio to job

Revision ID: f0d37ce6c095
Revises: 53dec4636bce
Create Date: 2016-01-29 20:35:43.118787

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f0d37ce6c095'
down_revision = '53dec4636bce'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('job', sa.Column('stderr', sa.Text(), nullable=True))
    op.add_column('job', sa.Column('stdout', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('job', 'stdout')
    op.drop_column('job', 'stderr')
