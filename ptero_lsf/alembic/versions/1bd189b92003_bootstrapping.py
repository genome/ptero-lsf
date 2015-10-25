"""bootstrapping

Revision ID: 1bd189b92003
Revises: 
Create Date: 2015-10-21 15:50:33.428529

"""

# revision identifiers, used by Alembic.
revision = '1bd189b92003'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.create_table('job',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('command', sa.Text(), nullable=False),
        sa.Column('options', postgresql.JSON(), nullable=True),
        sa.Column('rlimits', postgresql.JSON(), nullable=True),
        sa.Column('cwd', sa.Text(), nullable=False),
        sa.Column('environment', postgresql.JSON(), nullable=True),
        sa.Column('umask', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('lsf_job_id', sa.Integer(), nullable=True),
        sa.Column('poll_after', sa.DateTime(), nullable=True),
        sa.Column('polling_interval', sa.Interval(), nullable=False),
        sa.Column('user', sa.Text(), nullable=False),
        sa.Column('webhooks', postgresql.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_job'))
    )
    op.create_index(op.f('ix_job_lsf_job_id'), 'job', ['lsf_job_id'], unique=False)
    op.create_index(op.f('ix_job_poll_after'), 'job', ['poll_after'], unique=False)
    op.create_index(op.f('ix_job_user'), 'job', ['user'], unique=False)
    op.create_table('job_status_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('job_id', postgresql.UUID(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.Text(), nullable=False),
        sa.Column('lsf_primary_status', sa.Text(), nullable=True),
        sa.Column('lsf_status_set', postgresql.JSON(), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['job_id'], [u'job.id'], name=op.f('fk_job_status_history_job_id_job')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_job_status_history'))
    )
    op.create_index(op.f('ix_job_status_history_lsf_primary_status'), 'job_status_history', ['lsf_primary_status'], unique=False)
    op.create_index(op.f('ix_job_status_history_status'), 'job_status_history', ['status'], unique=False)


def downgrade():
    raise NotImplementedError("Cannot undo bootstrapping");

# flake8: noqa
