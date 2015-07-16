from . import celery_tasks  # noqa
from . import models
from ptero_lsf.implementation import statuses
import datetime


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
