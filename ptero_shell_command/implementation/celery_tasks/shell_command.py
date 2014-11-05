import celery
import subprocess
import os
import pwd

__all__ = ['ShellCommandTask']

class PreExecFailed(Exception): pass

class ShellCommandTask(celery.Task):
    def run(self, command_line, environment=None, stdin=None, callbacks=None, username=None):
        self.callback('begun', callbacks, jobId=self.request.id)

        try:
            p = subprocess.Popen(command_line, env=environment, close_fds=True,
                preexec_fn=lambda :self._setup_execution_environment(username),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # XXX We cannot use communicate for real, because communicate buffers
            # the data in memory until the process ends.
            stdout_data, stderr_data = p.communicate(stdin)

            exit_code = p.wait()

            self.callback('ended', callbacks, exitCode=exit_code,
                    stdout=stdout_data, stderr=stderr_data,
                    jobId=self.request.id)

            return exit_code == 0
        except PreExecFailed as e:
            self.callback('error', callbacks, jobId=self.request.id, errorMessage=e.message)
            return False

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

    def _setup_execution_environment(self, username):
        try:
            pw_ent = pwd.getpwnam(username)
        except KeyError as e:
            raise PreExecFailed(e.message)

        uid = pw_ent[2]
        self._set_uid(uid)

    def _set_uid(self, uid):
        try:
            os.setreuid(uid, uid)
        except OSError as e:
            raise PreExecFailed('Failed to setreuid: ' + e.strerror)
