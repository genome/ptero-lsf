import celery
import subprocess
import os
import pwd

__all__ = ['ShellCommandTask']

class PreExecFailed(Exception): pass

class ShellCommandTask(celery.Task):
    def run(self, command_line, umask, username, cwd=None, environment=None,
        stdin=None, callbacks=None):
        self.callback('begun', callbacks, jobId=self.request.id)

        if username == 'root':
            self.callback('error', callbacks, jobId=self.request.id,
                errorMessage='Refusing to execute job as root user')
            return False

        try:
            p = subprocess.Popen(command_line, env=environment, close_fds=True,
                preexec_fn=lambda :self._setup_execution_environment(cwd, umask, username),
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

    def _setup_execution_environment(self, cwd, umask, username):
        self._set_umask(umask)
        try:
            pw_ent = pwd.getpwnam(username)
        except KeyError as e:
            raise PreExecFailed(e.message)

        uid = pw_ent[2]
        self._set_uid(uid)
        self._set_cwd(cwd)

    def _set_umask(self, umask):
        if not umask == None:
            try:
                os.umask(umask)
            except TypeError as e:
                raise PreExecFailed('Failed to set umask: ' + e.message)

    def _set_uid(self, uid):
        try:
            os.setreuid(uid, uid)
        except OSError as e:
            raise PreExecFailed('Failed to setreuid: ' + e.strerror)

    def _set_cwd(self, cwd):
        if not cwd == None:
            try:
                os.chdir(cwd)
            except OSError as e:
                raise PreExecFailed('chdir(%s): %s' % (cwd, e.strerror))
