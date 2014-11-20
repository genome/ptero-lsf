import errno
import os
import psutil
import signal
import subprocess
import sys
import time


NUM_WORKERS = 4


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
        return 5

def this_dir():
    return os.path.dirname(__file__)

def procfile_path():
    if os.environ.get('TEST_WITH_ROOT_WORKERS'):
        return os.path.join(this_dir(), 'scripts', 'Procfile-with-sudo')
    else:
        return os.path.join(this_dir(), 'scripts', 'Procfile')

def service_command_line():
    return ['honcho', '-f', procfile_path(), 'start',
            '-c', 'worker=%s' % NUM_WORKERS]


def setUp():
    global instance

    logdir = 'var/log'
    mkdir_p(logdir)
    outlog = open(os.path.join(logdir, 'honcho.out'), 'w')
    errlog = open(os.path.join(logdir, 'honcho.err'), 'w')

    if not os.environ.get('SKIP_PROCFILE'):
        instance = psutil.Popen(service_command_line(),
                shell=False, stdout=outlog, stderr=errlog)
        time.sleep(wait_time())
        if instance.poll() is not None:
            raise RuntimeError("honcho instance terminated prematurely")

def signal_processes(processes, sig):
    signaled_someone = False
    for p in processes:
        try:
            if p.uids()[0] == 0:
                signaled_someone |= sudo_send_signal(p,sig)
            else:
                signaled_someone |= send_signal(p,sig)
        except psutil.NoSuchProcess:
            pass
    return signaled_someone

def send_signal(process,signal):
    try:
        process.send_signal(signal)
        return True
    except psutil.NoSuchProcess:
        pass
    return False

def sudo_send_signal(process,signal):
    command = ["sudo", "kill", "-" + str(signal), str(process.pid)]
    try:
        subprocess.check_call(command)
        return True
    except:
        pass
    return False

def get_descendents():
    return psutil.Process(instance.pid).children(recursive=True)

def cleanup():
    descendents = get_descendents()

    instance.send_signal(signal.SIGINT)
    try:
        instance.wait(timeout=2)
    except psutil.TimeoutExpired:
        instance.send_signal(signal.SIGTERM)
        instance.wait(timeout=3)

    if not signal_processes(descendents, signal.SIGINT):
        return

    time.sleep(3)
    signal_processes(descendents, signal.SIGKILL)

# NOTE If this doesn't run then honcho will be orphaned...
def tearDown():
    if not os.environ.get('SKIP_PROCFILE'):
        cleanup()
