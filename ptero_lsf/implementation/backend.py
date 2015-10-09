from . import celery_tasks  # noqa
from . import models
from ptero_lsf.implementation import statuses
import datetime
import logging
import os
from pprint import pformat


LOG = logging.getLogger(__name__)


try:
    import lsf
    from lsf.exceptions import InvalidJob
except ImportError:
    if int(os.environ.get("PTERO_LSF_NON_WORKER", "0")):
        LOG.info("Failed to import lsf library, this is OK since "
            "this process is not a worker that needs to access lsf")
    else:
        raise


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

    def create_job(self, command, job_id, options=None, rLimits=None,
            webhooks=None, pollingInterval=900, cwd='/tmp', environment=None,
            umask=None, user=None):
        polling_interval = datetime.timedelta(seconds=pollingInterval)

        if umask is not None:
            umask = int(umask, 8)

        job = models.Job(id=job_id, command=command, options=options,
                rlimits=rLimits, webhooks=webhooks,
                polling_interval=polling_interval, cwd=cwd,
                environment=environment, umask=umask, user=user)
        self.session.add(job)

        LOG.debug("Setting status of job (%s) to 'new'", job.id)
        job.set_status(statuses.new)

        LOG.debug("Commiting job (%s) to DB", job.id)
        self.session.commit()
        LOG.debug("Job (%s) committed to DB", job.id)

        LOG.info("Submitting Celery LSFTask for job (%s)",
                job.id)
        self.lsf.delay(job.id)

        return job.as_dict

    def get_job(self, job_id):
        job = self.session.query(models.Job).get(job_id)
        if job:
            return job.as_dict

    def update_job_status(self, job_id):
        LOG.debug('Looking up job (%s) in DB', job_id)
        service_job = self.session.query(
            models.Job).get(job_id)
        LOG.debug('DB says Job (%s) has lsf id [%s]',
            job_id, service_job.lsf_job_id)

        if service_job.lsf_job_id is None:
            service_job.set_status(statuses.errored,
                    message='LSF job id for job (%s) is None' % job_id)
            self.session.rollback()
            return False

        else:
            LOG.info("Querying LSF about job (%s) with lsf id [%s]",
                    job_id, service_job.lsf_job_id)
            lsf_job = lsf.get_job(service_job.lsf_job_id)

            try:
                job_data = lsf_job.as_dict
            except InvalidJob:
                LOG.exception("Exception occured while converting lsf"
                    " job to dictionary")
                self.session.rollback()
                return False

            LOG.info("Setting status of job (%s) to %s", job_id,
                    pformat(job_data['statuses']))
            service_job.update_status(job_data['statuses'])

        self.session.commit()
        return True
