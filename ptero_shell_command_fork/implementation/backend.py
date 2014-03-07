from . import celery_tasks


class Backend(object):
    def __init__(self, celery_app):
        self.celery_app = celery_app

    def cleanup(self):
        pass

    def create_job(self, command_line, environment={}, logging=None):
        task = self.celery_app.tasks[
'ptero_shell_command_fork.implementation.celery_tasks.shell_command.ShellCommandTask'
            ].delay(command_line, environment=environment,
                    logging_configuration=logging)

        return task.id
