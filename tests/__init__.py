import errno
import os
import psutil
import signal
import subprocess
import sys
import time

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


def setUp():
    global instance

    logdir = 'var/log'
    mkdir_p(logdir)
    outlog = open(os.path.join(logdir, 'honcho.out'), 'w')
    errlog = open(os.path.join(logdir, 'honcho.err'), 'w')

    if not os.environ.get('SKIP_PROCFILE'):
        instance = subprocess.Popen(service_command_line(),
                shell=False, stdout=outlog, stderr=errlog)
        time.sleep(wait_time())
        os.system("ps -efl > var/log/ps-alt.out") # XXX debug
        if instance.poll():
            raise RuntimeError("honcho instance terminated prematurely")


def reap_processes(processes):
    if os.environ.get('TRAVIS'):
        time.sleep(5)
        for p in processes:
            try:
                p.send_signal(signal.SIGINT)
            except psutil.NoSuchProcess:
                pass

        time.sleep(0.2)
        for p in processes:
            try:
                p.kill()
            except psutil.NoSuchProcess:
                pass


def get_children(pid):
    return psutil.Process(pid).get_children(recursive=True)


# XXX If this doesn't run then honcho will be orphaned...
def tearDown():
    children = get_children(instance.pid)
    reap_processes(children)
    instance.send_signal(signal.SIGINT)
