from ptero_lsf.api import application
from ptero_common.logging_configuration import configure_web_logging
import argparse
import logging
import os

app = application.create_app()
configure_web_logging("LSF")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true', default=False)
    return parser.parse_args()


if __name__ == '__main__':
    import signal
    signal.signal(signal.SIGTERM, signal.getsignal(signal.SIGINT))
    args = parse_args()
    app.run(
        host='0.0.0.0',
        port=os.environ['PTERO_LSF_PORT'], debug=args.debug)
