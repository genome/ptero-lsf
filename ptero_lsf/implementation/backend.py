from . import celery_tasks  # noqa
from . import models
from ptero_lsf.implementation import statuses
import datetime
import logging
import os


LOG = logging.getLogger(__name__)


try:
    import lsf
    from lsf.exceptions import InvalidJob
except ImportError as e:
    if int(os.environ.get("PTERO_LSF_NON_WORKER", "0")):
        LOG.info("Failed to import lsf library, this is OK since "
            "this process is not a worker that needs to access lsf")
    else:
        raise e


class Backend(object):
    def __init__(self, session, celery_app):
        self.session = session
        self.celery_app = celery_app

    def cleanup(self):
        self.session.rollback()

    @property
    def lsf(self):
        return self.celery_app.tasks[
'ptero_lsf.implementation.celery_tasks.lsf_task.LSFTask'
        ]

    def create_job(self, command, options=None, rLimits=None, webhooks=None,
                   pollingInterval=900, cwd='/tmp', environment=None,
                   umask=None, user=None):
        polling_interval = datetime.timedelta(seconds=pollingInterval)

        if umask is not None:
            umask = int(umask, 8)

        job = models.Job(command=command, options=options, rlimits=rLimits,
                webhooks=webhooks, polling_interval=polling_interval, cwd=cwd,
                environment=environment, umask=umask, user=user)
        self.session.add(job)
        job.set_status(statuses.new)
        self.session.commit()

        self.lsf.delay(job.id)

        return job.id, job.as_dict

    def get_job(self, job_id):
        job = self.session.query(models.Job).get(job_id)
        if job:
            return job.as_dict

    def update_job_status(self, job_id):
        LOG.debug('Updating status for service job: %s' % job_id)
        service_job = self.session.query(
            models.Job).get(job_id)
        LOG.debug('Serivce job %s has lsf id %s' % (
            job_id, service_job.lsf_job_id))

        if service_job.lsf_job_id is None:
            service_job.set_status(statuses.errored,
                    message='LSF job id for job %s is None' % job_id)
            self.session.rollback()
            return False

        else:
            lsf_job = lsf.get_job(service_job.lsf_job_id)

            try:
                job_data = lsf_job.as_dict
            except InvalidJob as e:
                LOG.exception(e)
                self.session.rollback()
                return False

            service_job.update_status(job_data['statuses'])

        self.session.commit()
        return True
