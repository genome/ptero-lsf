from .. import models
from multiprocessing import Pipe, Process
from celery.utils.log import get_task_logger
import celery
import os

__all__ = ['LSFTask']


LOG = get_task_logger(__name__)


class SubmitError(Exception):
    pass


class LSFTask(celery.Task):
    def run(self, job_id):
        session = celery.current_app.Session()
        service_job = session.query(models.Job).get(job_id)

        try:
            lsf_job_id = _fork_and_submit_job(service_job)

            service_job.lsf_job_id = lsf_job_id
            service_job.set_status('SUBMITTED')

        except Exception as e:
            LOG.exception('Error submitting job')
            service_job.set_status('ERRORED', message=e.message)

        session.commit()


def _submit_job(child_pipe, parent_pipe, service_job):
    try:
        parent_pipe.close()

        os.chdir(service_job.cwd)

        lsf_job = service_job.submit()
        child_pipe.send(lsf_job.job_id)
    except Exception as e:
        child_pipe.send(str(e))

    child_pipe.close()


def _fork_and_submit_job(service_job):
    parent_pipe, child_pipe = Pipe()
    try:
        p = Process(target=_submit_job,
                    args=(child_pipe, parent_pipe, service_job,))
        p.start()

    except:
        parent_pipe.close()
        raise
    finally:
        child_pipe.close()

    try:
        p.join()

        result = parent_pipe.recv()
        if isinstance(result, basestring):
            raise SubmitError(result)

    except EOFError:
        raise SubmitError('Unknown exception submitting job')
    finally:
        parent_pipe.close()

    return result
