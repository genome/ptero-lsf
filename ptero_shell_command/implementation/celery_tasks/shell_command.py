import celery
import subprocess

__all__ = ['ShellCommandTask']


class ShellCommandTask(celery.Task):
    def run(self, command_line, environment=None, stdin=None, callbacks=None):
        self.callback('begun', callbacks, jobId=self.request.id)

        p = subprocess.Popen(command_line, env=environment, close_fds=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # XXX We cannot use communicate for real, because communicate buffers
        # the data in memory until the process ends.
        stdout_data, stderr_data = p.communicate(stdin)

        exit_code = p.wait()

        self.callback('ended', callbacks, exitCode=exit_code,
                stdout=stdout_data, stderr=stderr_data,
                jobId=self.request.id)

        return {'exit_code': exit_code}

    def callback(self, status, callbacks, **kwargs):
        if callbacks is None:
            return

        if status in callbacks:
            task = self._get_http_task()
            task.delay(callbacks[status], status=status, **kwargs)

    def _get_http_task(self):
        return celery.current_app.tasks[
'ptero_shell_command.implementation.celery_tasks.http_callback.HTTPCallbackTask'
        ]
