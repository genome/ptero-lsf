import celery
import os
import pwd
import subprocess

__all__ = ['LSFTask']

class PreExecFailed(Exception): pass

class LSFTask(celery.Task):
    def run(self, command_line, umask, user, working_directory,
        environment=None, stdin=None, callbacks=None):
        self.callback('begun', callbacks, jobId=self.request.id)

        if user == 'root':
            self.callback('error', callbacks, jobId=self.request.id,
                errorMessage='Refusing to execute job as root user')
            return False

        try:
            p = subprocess.Popen(command_line, env=environment, close_fds=True,
                preexec_fn=lambda :self._setup_execution_environment(umask, user, working_directory),
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
        except OSError as e:
            if e.errno == 2:
                self.callback('error', callbacks, jobId=self.request.id,
                    errorMessage='Command not found: %s' % command_line[0])
            else:
                raise e
            return False

    def callback(self, status, callbacks, **kwargs):
        if callbacks is None:
            return

        if status in callbacks:
            task = self._get_http_task()
            task.delay(callbacks[status], status=status, **kwargs)

    def _get_http_task(self):
        return celery.current_app.tasks[
'ptero_lsf.implementation.celery_tasks.http_callback.HTTPCallbackTask'
        ]

    def _setup_execution_environment(self, umask, user, working_directory):
        self._set_uid(user)
        self._set_umask(umask)
        self._set_working_directory(working_directory)

    def _set_umask(self, umask):
        if not umask == None:
            try:
                os.umask(umask)
            except TypeError as e:
                raise PreExecFailed('Failed to set umask: ' + e.message)

    def _set_uid(self, user):
        try:
            pw_ent = pwd.getpwnam(user)
        except KeyError as e:
            raise PreExecFailed(e.message)

        try:
            os.setreuid(pw_ent.pw_uid, pw_ent.pw_uid)
        except OSError as e:
            raise PreExecFailed('Failed to setreuid: ' + e.strerror)

    def _set_working_directory(self, working_directory):
        try:
            os.chdir(working_directory)
        except OSError as e:
            raise PreExecFailed(
                'chdir(%s): %s' % (working_directory, e.strerror))
