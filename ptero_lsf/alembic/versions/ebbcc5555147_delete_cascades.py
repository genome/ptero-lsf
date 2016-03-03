"""delete_cascades

Revision ID: ebbcc5555147
Revises: f0d37ce6c095
Create Date: 2016-03-03 03:26:33.466834

"""

# revision identifiers, used by Alembic.
revision = 'ebbcc5555147'
down_revision = 'f0d37ce6c095'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_index(op.f('ix_job_status_history_job_id'), 'job_status_history', ['job_id'], unique=False)
    op.drop_constraint(u'fk_job_status_history_job_id_job', 'job_status_history', type_='foreignkey')
    op.create_foreign_key(op.f('fk_job_status_history_job_id_job'), 'job_status_history', 'job', ['job_id'], ['id'], ondelete='CASCADE')


def downgrade():
    op.drop_constraint(op.f('fk_job_status_history_job_id_job'), 'job_status_history', type_='foreignkey')
    op.create_foreign_key(u'fk_job_status_history_job_id_job', 'job_status_history', 'job', ['job_id'], ['id'])
    op.drop_index(op.f('ix_job_status_history_job_id'), table_name='job_status_history')

# flake8: noqa
