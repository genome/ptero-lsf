from . import celery_tasks


class Backend(object):
    def __init__(self, celery_app):
        self.celery_app = celery_app

    def cleanup(self):
        pass

    @property
    def shell_command(self):
        return self.celery_app.tasks[
'ptero_shell_command_fork.implementation.celery_tasks.shell_command.ShellCommandTask'
        ]

    def create_job(self, command_line, environment={}, logging=None):
        task = self.shell_command.delay(command_line, environment=environment,
                    logging_configuration=logging)

        return task.id

    def get_job_status(self, job_id):
        task = self.shell_command.AsyncResult(job_id)

        return _job_status_from_task(task)

_JOB_STATUS_FROM_TASK_STATUS = {
    'SUCCESS': 'succeeded',
}
def _job_status_from_task(task):
    if task is None:
        return None
    return _JOB_STATUS_FROM_TASK_STATUS[task.status]
