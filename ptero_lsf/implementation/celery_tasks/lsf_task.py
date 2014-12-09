from .. import models
from celery.utils.log import get_task_logger
import celery
import os
import subprocess

__all__ = ['LSFTask']


LOG = get_task_logger(__name__)


class CommunicateLSFid(RuntimeError):
    pass

class PreExecFailure(RuntimeError):
    pass


class LSFTask(celery.Task):
    def run(self, job_id):
        session = celery.current_app.Session()
        service_job = session.query(models.Job).get(job_id)

        try:
            lsf_job_id = _submit_job(service_job)

            service_job.lsf_job_id = lsf_job_id
            service_job.set_status('SUBMITTED')

        except Exception as e:
            LOG.exception('Error submitting job')
            service_job.set_status('ERRORED', message=e.message)

        session.commit()


def _submit_job(service_job):
    try:
        p = subprocess.Popen(['true'], close_fds=False, stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                preexec_fn=lambda: _preexec_fn(service_job))

        exit_code = p.wait()

        raise RuntimeError('Got exit code: %s' % exit_code)

    except CommunicateLSFid as e:
        return int(e.message)


def _preexec_fn(service_job):
    try:
        os.chdir(service_job.cwd)
        lsf_job = service_job.submit()

    except Exception as e:
        raise PreExecFailure(str(e))

    raise CommunicateLSFid(lsf_job.job_id)
