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

def process_exists(process):
    try:
        p = psutil.Process(process.pid)
        return 1
    except:
        return 0

def check_processes(cmdlines, processes):
    time.sleep(5)
    f = open('var/log/pids.out', 'w')
    f.write("PIDs:\n")
    for p in processes:
        f.write("%d %s\n" % (process_exists(p), p.pid))
        for x in cmdlines[p.pid]:
            f.write("\t%s\n" % x)
    f.close()

# XXX If this doesn't run then honcho will be orphaned...
def tearDown():
    p = psutil.Process(instance.pid)
    children = p.get_children(recursive=True)
    cmdlines = {} # cache these values
    for p in children:
        cmdlines[p.pid] = p.cmdline()
    instance.send_signal(signal.SIGINT)
    check_processes(cmdlines, children) # XXX debug
