from . import celery_tasks
from . import models


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

    def create_job(self, command, options):
        job = models.Job(command=command, options=options, status='NEW')
        self.session.add(job)
        self.session.commit()

        task = self.lsf.delay(job.id, command, options)

        return job.id, job.as_dict

    def get_job(self, job_id):
        job = self.session.query(models.Job).get(job_id)
        if job:
            return job.as_dict
