import errno
import os


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def setUp():
    if 'PTERO_LSF_TEST_NETWORK_TEMP' in os.environ:
        mkdir_p(os.environ['PTERO_LSF_TEST_NETWORK_TEMP'])
