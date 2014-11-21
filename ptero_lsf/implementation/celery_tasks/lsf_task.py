import celery
import lsf
import os
import pwd
import subprocess

__all__ = ['LSFTask']


class LSFTask(celery.Task):
    def run(self, command):
        job = lsf.submit(str(command))
        return job.job_id
