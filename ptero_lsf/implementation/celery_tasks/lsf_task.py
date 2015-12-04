import celery
from ptero_common import nicer_logging


LOG = nicer_logging.getLogger(__name__)


__all__ = ['LSFSubmit', 'LSFKill']


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
        finally:
            if backend is not None:
                backend.cleanup()


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
        finally:
            if backend is not None:
                backend.cleanup()
