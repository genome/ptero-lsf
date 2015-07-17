import celery
import logging

__all__ = ['UpdateJobStatus']

LOG = logging.getLogger(__name__)


class UpdateJobStatus(celery.Task):
    def run(self, job_id):
        LOG.debug('Updating job status for %s' % job_id)
        backend = celery.current_app.factory.create_backend()
        backend.update_job_status(job_id)
