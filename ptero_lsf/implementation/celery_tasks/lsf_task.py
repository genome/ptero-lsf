from .. import models
from sqlalchemy import func
import celery
import os
import pwd
import subprocess

__all__ = ['LSFTask']


class LSFTask(celery.Task):
    def run(self, job_id):
        session = celery.current_app.Session()
        service_job = session.query(models.Job).get(job_id)

        lsf_job = service_job.submit()

        service_job.lsf_job_id = lsf_job.job_id
        service_job.set_status('SUBMITTED')
        service_job.update_poll_after()
        service_job.trigger_webhook('submit')
        session.commit()
