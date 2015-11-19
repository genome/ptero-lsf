from .. import models
from sqlalchemy import func
import celery
from ptero_common import nicer_logging
import os


LOG = nicer_logging.getLogger(__name__)

MAX_FAILS = os.environ.get("PTERO_LSF_MAX_FAILED_UPDATE_ATTEMPTS", 5)


class PollActiveJobs(celery.Task):
    def run(self):
        LOG.info('Polling DB for active jobs')
        backend = celery.current_app.factory.create_backend()
        session = backend.session
        jobs = session.query(models.Job).filter(
                (models.Job.poll_after <= func.now()) &
                ~(models.Job.awaiting_update) &
                (models.Job.failed_update_count < MAX_FAILS)
                ).all()

        job_ids_to_update = []
        for job in jobs:
            job_ids_to_update.append(job.id)
            job.awaiting_update = True
        session.commit()

        for job_id in job_ids_to_update:
            LOG.info('Submitting Celery UpdateJobStatus for job (%s)', job_id,
                extra={'jobId': job_id})
            self.update_job_status.delay(job_id)

    @property
    def update_job_status(self):
        return celery.current_app.tasks[
            'ptero_lsf.implementation.celery_tasks.job_status.UpdateJobStatus'
        ]
