from . import celery_tasks


class Backend(object):
    def __init__(self, celery_app):
        self.celery_app = celery_app

    def cleanup(self):
        pass

    @property
    def lsf(self):
        return self.celery_app.tasks[
'ptero_lsf.implementation.celery_tasks.lsf_task.LSFTask'
        ]

    def create_job(self, command, options):
        task = self.lsf.delay(command, options)

        return task.id
