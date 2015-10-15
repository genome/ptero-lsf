import celery
from ptero_common import nicer_logging


LOG = nicer_logging.getLogger(__name__)


__all__ = ['UpdateJobStatus']


class UpdateJobStatus(celery.Task):
    def run(self, job_id):
        LOG.info('Updating job status for job (%s)', job_id,
                extra={'jobId': job_id})
        backend = celery.current_app.factory.create_backend()
        backend.update_job_status(job_id)
