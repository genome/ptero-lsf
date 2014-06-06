from ctypes import cdll # XXX debug
import errno
import os
import signal
import subprocess
import sys
import time

# Code from: http://www.evans.io/posts/killing-child-processes-on-parent-exit-prctl/
# Constant taken from http://linux.die.net/include/linux/prctl.h
PR_SET_PDEATHSIG = 1 # XXX debug

# Code from: http://www.evans.io/posts/killing-child-processes-on-parent-exit-prctl/
class PrCtlError(Exception): # XXX debug
    pass

instance = None

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def wait_time():
    if os.environ.get('TRAVIS'):
        return 10
    else:
        return 2


def procfile_path():
    return os.path.join(os.path.dirname(__file__),
            'scripts', 'Procfile')


def service_command_line():
    return ['honcho', '-f', procfile_path(), 'start']


# Code from: http://www.evans.io/posts/killing-child-processes-on-parent-exit-prctl/
def on_parent_exit(signame): # XXX debug
    """
    Return a function to be run in a child process which will trigger
    SIGNAME to be sent when the parent process dies
    """
    signum = getattr(signal, signame)
    def set_parent_exit_signal():
        # http://linux.die.net/man/2/prctl
        result = cdll['libc.so.6'].prctl(PR_SET_PDEATHSIG, signum)
        if result != 0:
            raise PrCtlError('prctl failed with error code %s' % result)
    return set_parent_exit_signal

def setUp():
    global instance

    logdir = 'var/log'
    mkdir_p(logdir)
    outlog = open(os.path.join(logdir, 'honcho.out'), 'w')
    errlog = open(os.path.join(logdir, 'honcho.err'), 'w')

    if not os.environ.get('SKIP_PROCFILE'):
        instance = subprocess.Popen(service_command_line(),
                shell=False, stdout=outlog, stderr=errlog,
                preexec_fn=on_parent_exit('SIGTERM')) # XXX debug
        time.sleep(wait_time())
        os.system("ps -efl > var/log/ps-alt.out") # XXX debug
        if instance.poll():
            raise RuntimeError("honcho instance terminated prematurely")

# XXX If this doesn't run then honcho will be orphaned...
def tearDown():
    instance.send_signal(signal.SIGINT)
