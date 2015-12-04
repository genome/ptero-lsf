import celery
from ptero_common import nicer_logging


LOG = nicer_logging.getLogger(__name__)


class PollActiveJobs(celery.Task):
    def run(self):
        LOG.info('Polling DB for active jobs')

        try:
            backend = celery.current_app.factory.create_backend()
            job_ids_to_update = backend.get_job_ids_to_update()

            for job_id in job_ids_to_update:
                LOG.info(
                    'Submitting Celery UpdateJobStatus for job (%s)',
                    job_id, extra={'jobId': job_id})
                self.update_job_status.delay(job_id)
        except:
            LOG.exception("Exception while trying to submit job (%s) to lsf",
                    job_id, extra={'jobId': job_id})
            raise
        finally:
            if backend is not None:
                backend.cleanup()

    @property
    def update_job_status(self):
        return celery.current_app.tasks[
            'ptero_lsf.implementation.celery_tasks.job_status.UpdateJobStatus'
        ]
