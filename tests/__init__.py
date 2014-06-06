import errno
import os
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

def setUp():
    mkdir_p('logs')
    loghandle = open('logs/honcho.out', 'w')
    global instance

    if not os.environ.get('SKIP_PROCFILE'):
        instance = subprocess.Popen(
                ['honcho', '-f', 'Procfile.dev', 'start'],
                shell=False, stdout=loghandle)
        time.sleep(wait_time())
        if instance.poll():
            raise RuntimeError("honcho instance terminated prematurely")

# XXX If this doesn't run then honcho will be orphaned...
def tearDown():
    instance.send_signal(signal.SIGINT)
