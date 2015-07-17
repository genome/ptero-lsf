from .. import models
import celery
from sqlalchemy import func
import logging

LOG = logging.getLogger(__name__)


class PollActiveJobs(celery.Task):
    def run(self):
        LOG.debug('Polling active jobs')
        backend = celery.current_app.factory.create_backend()
        session = backend.session
        job_ids = session.query(models.Job.id)\
                .filter(models.Job.poll_after <= func.now()).all()

        for job_id in job_ids:
            LOG.debug('Scheduling update for job %s' % job_id)
            self.update_job_status.delay(job_id)

    @property
    def update_job_status(self):
        return celery.current_app.tasks[
            'ptero_lsf.implementation.celery_tasks.job_status.UpdateJobStatus'
        ]
