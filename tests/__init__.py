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
        return 15
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
        if instance.poll() is not None:
            raise RuntimeError("honcho instance terminated prematurely")


def travis_ci_cleanup():
    grandchildren = get_grandchildren()
    descendents = get_descendents()

    if not signal_processes(grandchildren, signal.SIGINT):
        return

    time.sleep(1)
    if not signal_processes(descendents, signal.SIGINT):
        return

    time.sleep(3)
    signal_processes(descendents, signal.SIGKILL)


def signal_processes(processes, sig):
    signaled_someone = False
    for p in processes:
        try:
            p.send_signal(sig)
            signaled_someone = True
        except psutil.NoSuchProcess:
            pass

    return signaled_someone


def get_grandchildren():
    children = psutil.Process(instance.pid).get_children(recursive=False)
    grandchildren = []
    for child in children:
        grandchildren.extend(child.get_children(recursive=False))
    return grandchildren


def get_descendents():
    return psutil.Process(instance.pid).get_children(recursive=True)


# NOTE If this doesn't run then honcho will be orphaned...
def tearDown():
    if os.environ.get('TRAVIS'):
        travis_ci_cleanup()

    instance.send_signal(signal.SIGINT)
