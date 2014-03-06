import celery
import contextlib
import errno
import os
import subprocess
import sys

__all__ = ['ShellCommandTask']


class ShellCommandTask(celery.Task):
    def run(self, command_line, environment=None, stderr=None, stdin=None,
            stdout=None, callbacks=None):

        with open_files(stderr, stdin, stdout) as (err_fh, in_fh, out_fh):
            p = subprocess.Popen(command_line, env=environment, close_fds=True,
                    stderr=err_fh, stdin=in_fh, stdout=out_fh)
        return {'exit_code': p.wait()}


@contextlib.contextmanager
def open_files(stderr, stdin, stdout):
    make_path_to(stderr)
    make_path_to(stdout)
    make_path_to(stdin)

    stderr_fh = None
    stdin_fh = None
    stdout_fh = None
    try:
        if stderr:
            stderr_fh = open(stderr, 'a')
        if stdin:
            stdin_fh = open(stdin, 'r')
        if stdout:
            stdout_fh = open(stdout, 'a')
        else:
            stdout_fh = sys.stderr

        yield stderr_fh, stdin_fh, stdout_fh

    finally:
        if stderr_fh:
            stderr_fh.close()
        if stdin_fh:
            stdin_fh.close()
        if stdout_fh:
            stdout_fh.close()

def make_path_to(filename):
    if filename:
        if os.path.dirname(filename):
            mkdir_p(os.path.dirname(filename))

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

