from .. import models
import celery
import lsf
import os
import pwd
import subprocess

__all__ = ['LSFTask']


class LSFTask(celery.Task):
    def run(self, job_id, command, options):
        session = celery.current_app.Session()
        service_job = session.query(models.Job).get(job_id)

        lsf_job = lsf.submit(str(command), options=options)

        service_job.lsf_job_id = lsf_job.job_id
        session.commit()
