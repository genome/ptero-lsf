import celery
from ptero_common import nicer_logging


LOG = nicer_logging.getLogger(__name__)


__all__ = ['LSFTask', 'LSFSubmit', 'LSFKill']


class LSFTask(celery.Task):
    def run(self, job_id):
        LOG.warning("LSFTask is deprecated, issuing LSFSubmit for job (%s)",
                job_id, extra={'jobId': job_id})

        new_task = celery.current_app.tasks[
            'ptero_lsf.implementation.celery_tasks.lsf_task.LSFSubmit'
        ]
        new_task.delay(job_id)


class LSFSubmit(celery.Task):
    def run(self, job_id):
        LOG.info("Preparing to submit job (%s) to lsf", job_id,
                extra={'jobId': job_id})
        try:
            backend = celery.current_app.factory.create_backend()
            backend.submit_job_to_lsf(job_id)
        except:
            LOG.exception("Exception while trying to submit job (%s) to lsf",
                    job_id, extra={'jobId': job_id})
            raise


class LSFKill(celery.Task):
    def run(self, job_id):
        LOG.info("Preparing to kill job (%s)", job_id,
                extra={'jobId': job_id})
        try:
            backend = celery.current_app.factory.create_backend()
            backend.kill_lsf_job(job_id)
        except:
            LOG.exception("Exception while trying to kill job (%s)",
                    job_id, extra={'jobId': job_id})
            raise
