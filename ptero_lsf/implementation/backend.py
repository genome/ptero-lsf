from . import celery_tasks  # noqa
from . import models
from ptero_lsf.implementation import statuses
import datetime
import os
from sqlalchemy import func
from pprint import pformat
from ptero_common.server_info import get_server_info
from ptero_common import nicer_logging


LOG = nicer_logging.getLogger(__name__)

MAX_FAILS = os.environ.get("PTERO_LSF_MAX_FAILED_UPDATE_ATTEMPTS", 5)

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
    def __init__(self, session, celery_app, db_revision):
        self.session = session
        self.celery_app = celery_app
        self.db_revision = db_revision

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

        LOG.debug("Setting status of job (%s) to 'new'", job.id,
                extra={'jobId': job.id})
        job.set_status(statuses.new)

        LOG.debug("Commiting job (%s) to DB", job.id,
                extra={'jobId': job.id})
        self.session.commit()
        LOG.debug("Job (%s) committed to DB", job.id,
                extra={'jobId': job.id})

        LOG.info("Submitting Celery LSFTask for job (%s)",
                job.id, extra={'jobId': job.id})
        self.lsf.delay(job.id)

        return job.as_dict

    def get_job(self, job_id):
        job = self.session.query(models.Job).get(job_id)
        if job:
            return job.as_dict

    def update_job_status(self, job_id):
        LOG.debug('Looking up job (%s) in DB', job_id,
                extra={'jobId': job_id})
        service_job = self.session.query(
            models.Job).get(job_id)
        service_job.awaiting_update = False
        LOG.debug('DB says Job (%s) has lsf id [%s]',
                job_id, service_job.lsf_job_id,
                extra={'jobId': job_id, 'lsfJobId': service_job.lsf_job_id})

        if service_job.lsf_job_id is None:
            service_job.set_status(statuses.errored,
                    message='LSF job id for job (%s) is None' % job_id)
            self.session.commit()
            return False

        else:
            LOG.info("Querying LSF about job (%s) with lsf id [%s]",
                    job_id, service_job.lsf_job_id,
                    extra={'jobId': job_id, 'lsfJobId': service_job.lsf_job_id})
            lsf_job = lsf.get_job(service_job.lsf_job_id)

            try:
                job_data = lsf_job.as_dict
            except InvalidJob:
                # this could happen if you poll too quickly after launching the
                # job, lets allow for retrying a set number of times.
                service_job.failed_update_count += 1

                LOG.exception("Exception occured while converting lsf"
                    " job to dictionary")
                self.session.commit()
                return False

            LOG.info("Setting status of job (%s) to %s", job_id,
                    pformat(job_data['statuses']),
                    extra={'jobId': job_id, 'lsfJobId': service_job.lsf_job_id})
            service_job.update_status(job_data['statuses'])

        self.session.commit()
        return True

    def get_job_ids_to_update(self):
        jobs = self.session.query(models.Job).filter(
                (models.Job.poll_after <= func.now()) &
                (models.Job.failed_update_count < MAX_FAILS)
                ).all()

        job_ids_to_update = []
        for job in jobs:
            job_ids_to_update.append(job.id)
            if job.awaiting_update:
                LOG.warning("Awaiting update already set to True for job (%s)",
                        job.id, extra={'jobID': job.id})
            else:
                job.awaiting_update = True
        self.session.commit()

        return job_ids_to_update

    def server_info(self):
        result = get_server_info(
                'ptero_lsf.implementation.celery_app')
        result['databaseRevision'] = self.db_revision
        return result
