from ...base import BaseAPITest
from ptero_shell_command_fork.api import application
import os
import signal
import subprocess
import sys
import time


__all__ = ['DeferredAPITest']


# The unittest module doesn't provide conditional failure/success tear down.
# The cleanest way to know about a test failure, appears to be overriding the
# exception class used for failures.
_CURRENT_TEST_FAILED = False
class DeferredAPIFailureException(AssertionError):
    def __init__(self, *args, **kwargs):
        global _CURRENT_TEST_FAILED
        _CURRENT_TEST_FAILED = True
        super(DeferredAPIFailureException, self).__init__(*args, **kwargs)


_TERMINATE_WAIT_TIME = 0.1


class DeferredAPITest(BaseAPITest):
    failureException = DeferredAPIFailureException

    def create_wsgi_app(self):
        return application.create_app(purge=True)

    def setUp(self):
        global _CURRENT_TEST_FAILED
        _CURRENT_TEST_FAILED = False
        os.environ.setdefault('CELERY_BROKER_URL', 'amqp://')
        os.environ.setdefault('CELERY_RESULT_BACKEND', 'redis://')
        super(DeferredAPITest, self).setUp()

        self._workers = []

    def tearDown(self):
        self.stop_workers()

        if _CURRENT_TEST_FAILED:
            self._write_worker_output()

    def start_worker(self):
        self._workers.append(self._create_new_worker())

    def wait(self):
        time.sleep(self._wait_sleep_time)

    @property
    def _wait_sleep_time(self):
        return 10

    def stop_workers(self):
        self._terminate_workers()
        time.sleep(_TERMINATE_WAIT_TIME)
        self._kill_remaining_workers()


    def _create_new_worker(self):
        return subprocess.Popen(self._worker_command_line, close_fds=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    @property
    def _worker_command_line(self):
        return ['celery', 'worker', '--concurrency', '1',
                '-A', 'ptero_shell_command_fork.implementation.celery_app']

    def _terminate_workers(self):
        for worker in self._workers:
            worker.terminate()

    def _write_worker_output(self):
        for worker in self._workers:
            sys.stdout.write(worker.stdout.read())
            sys.stderr.write(worker.stderr.read())

    def _kill_remaining_workers(self):
        returncodes = [w.poll() for w in self._workers]

        for rc, worker in zip(returncodes, self._workers):
            if rc is None:
                print 'Worker (%d) is still running after TERM, KILLing' % worker.pid
                worker.kill()
                new_rc = worker.wait()
                if new_rc not in {-signal.SIGTERM, -signal.SIGKILL}:
                    self._raise_worker_exit_error(new_rc)

            elif rc != -signal.SIGTERM:
                self._raise_worker_exit_error(rc)

    def _raise_worker_exit_error(self, returncode):
        raise ValueError('Worker exited with unexpected return code (%d).'
                % returncode)
