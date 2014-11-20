from . import celery_tasks


class Backend(object):
    def __init__(self, celery_app):
        self.celery_app = celery_app

    def cleanup(self):
        pass

    @property
    def lsf(self):
        return self.celery_app.tasks[
'ptero_lsf.implementation.celery_tasks.lsf.LSFTask'
        ]

    def create_job(self, command_line, umask, user, working_directory,
        environment={}, stdin=None, callbacks=None):
        task = self.lsf.delay(command_line, umask, user, working_directory,
                environment=environment, stdin=stdin, callbacks=callbacks)

        return task.id

    def get_job_status(self, job_id):
        task = self.lsf.AsyncResult(job_id)

        return _job_status_from_task(task)

def _job_status_from_task(task):
    if task is None:
        return None

    state = task.state
    if state == 'SUCCESS':
        if task.result:
            return 'succeeded'
        else:
            return 'failed'

    elif state == 'STARTED':
        return 'running'

    elif state == 'PENDING':
        return 'pending'
