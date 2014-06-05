import os
import signal
import subprocess
import sys
import time

instances = {}

_TERMINATE_WAIT_TIME = 0.1

def setUp():
    DEVNULL = open(os.devnull, 'wb')

    procfile = 'Procfile.dev'
    if os.environ.get('TRAVIS'):
        procfile = 'Procfile'

    if not os.environ.get('SKIP_PROCFILE'):
        instances['honcho'] = subprocess.Popen(
                ['honcho', '-f', procfile, 'start'],
                shell=False, stdout=DEVNULL, stderr=DEVNULL)
        time.sleep(2)
        if instances['honcho'].poll():
            raise Exception("honcho instance terminated prematurely")

# XXX If this doesn't run then honcho will be orphaned...
def tearDown():
    for instance in instances.values():
        instance.send_signal(signal.SIGINT)
