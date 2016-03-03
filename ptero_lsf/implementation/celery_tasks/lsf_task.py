import celery
from ptero_common import nicer_logging


LOG = nicer_logging.getLogger(__name__)
MIN = 60
DELAYS = [1, 5, 10, 30, 60, 2 * MIN, 4 * MIN, 10 * MIN, 30 * MIN, 60 * MIN]
DELAYS.extend([60 * MIN for i in range(72)])


__all__ = ['LSFSubmit', 'LSFKill', 'LSFKillByID']


class LSFSubmit(celery.Task):
    ignore_result = True

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
    """ DEPRECATED: Remove after LSFKillByID has been deployed """
    ignore_result = True
    max_retries = len(DELAYS)

    def run(self, job_id):
        LOG.info("Preparing to kill job (%s)", job_id,
                extra={'jobId': job_id})
        try:
            backend = celery.current_app.factory.create_backend()
            backend.kill_job(job_id)
        except Exception as exc:
            delay = DELAYS[self.request.retries]
            LOG.exception("Exception while trying to kill job (%s) "
                    "retrying in %s seconds.  Attempt %d of %d.",
                    job_id, delay, self.request.retries + 1,
                    self.max_retries + 1, extra={'jobId': job_id})
            self.retry(exc=exc, countdown=delay)
        finally:
            if backend is not None:
                backend.cleanup()


class LSFKillByID(celery.Task):
    ignore_result = True
    max_retries = len(DELAYS)

    def run(self, job_id, lsf_job_id):
        LOG.info("Preparing to kill job (%s) with lsf job id (%s)",
                job_id, lsf_job_id, extra={'jobId': job_id})
        try:
            backend = celery.current_app.factory.create_backend()
            backend.kill_lsf_job(lsf_job_id)
        except Exception as exc:
            delay = DELAYS[self.request.retries]
            LOG.exception("Exception while trying to kill job (%s) with lsf "
                    "job id (%s) retrying in %s seconds.  Attempt %d of %d.",
                    job_id, lsf_job_id, delay, self.request.retries + 1,
                    self.max_retries + 1, extra={'jobId': job_id})
            self.retry(exc=exc, countdown=delay)
        finally:
            if backend is not None:
                backend.cleanup()
