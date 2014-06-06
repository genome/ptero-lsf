import os
import signal
import subprocess
import sys
import time


LOOP_PERIOD = 0.05

def webserver_path():
    return os.path.join(os.path.dirname(__file__), 'web_service.py')

sys.stderr.write('Wrapping web server for coverage collection\n')
child_process = subprocess.Popen(['coverage', 'run', webserver_path()])


def term_handler(signum, frame):
    sys.stderr.write('Sending SIGINT to wrapped coverage process')
    child_process.send_signal(signal.SIGINT)

    def kill_child(signum, frame):
        if child_process.poll() is None:
            child_process.kill()

    signal.signal(signal.SIGALRM, kill_child)
    signal.alarm(10)

signal.signal(signal.SIGINT, term_handler)
signal.signal(signal.SIGTERM, term_handler)


while True:
    time.sleep(LOOP_PERIOD)
    if child_process.poll() is not None:
        break
