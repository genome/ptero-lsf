#!/usr/bin/env python

from __future__ import print_function
from flask import Flask, request
import argparse
import signal
import sys


_RESPONSE_CODES = []
def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stop-after', type=int, default=10)
    parser.add_argument('--response-codes', nargs='+', type=int)

    arguments = parser.parse_args()

    global _RESPONSE_CODES
    _RESPONSE_CODES = list(reversed(arguments.response_codes))

    return arguments

# This isn't great, but it's the best we can do with Flask:
# http://stackoverflow.com/questions/2838244/get-open-tcp-port-in-python
# http://stackoverflow.com/questions/5085656/how-to-get-the-current-port-number-in-flask
def get_open_port():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost',0))
    port = s.getsockname()[1]
    s.close()
    return port

def next_response_code():
    response_code = _RESPONSE_CODES.pop()
    if not _RESPONSE_CODES:
        shutdown_server()
    return response_code


app = Flask(__name__)


@app.route('/', methods=['PUT'])
def log_request():
    print(request.data)
    return '', next_response_code()


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


if __name__ == '__main__':
    arguments = parse_arguments()
    signal.alarm(arguments.stop_after)
    port = get_open_port()
    print(port, file=sys.stderr)
    app.run(port=port)
