from .. import models
from sqlalchemy import func
import celery
import logging

LOG = logging.getLogger(__name__)


class PollActiveJobs(celery.Task):
    def run(self):
        LOG.info('Polling DB for active jobs')
        backend = celery.current_app.factory.create_backend()
        session = backend.session
        job_ids = session.query(models.Job.id)\
                .filter(models.Job.poll_after <= func.now()).all()

        for job_id, in job_ids:
            LOG.info('Submitting Celery UpdateJobStatus for job (%s)', job_id)
            self.update_job_status.delay(job_id)
        session.commit()

    @property
    def update_job_status(self):
        return celery.current_app.tasks[
            'ptero_lsf.implementation.celery_tasks.job_status.UpdateJobStatus'
        ]
