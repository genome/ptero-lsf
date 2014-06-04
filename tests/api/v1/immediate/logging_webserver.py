#!/usr/bin/env python

from flask import Flask, request
import argparse
import signal


_RESPONSE_CODES = []
def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5112)
    parser.add_argument('--stop-after', type=int, default=10)
    parser.add_argument('--response-codes', nargs='+', type=int)

    arguments = parser.parse_args()

    global _RESPONSE_CODES
    _RESPONSE_CODES = list(reversed(arguments.response_codes))

    return arguments

def next_response_code():
    response_code = _RESPONSE_CODES.pop()
    if not _RESPONSE_CODES:
        shutdown_server()
    return response_code


app = Flask(__name__)


@app.route('/', methods=['PUT'])
def log_request():
    print request.data
    return '', next_response_code()


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


if __name__ == '__main__':
    arguments = parse_arguments()
    signal.alarm(arguments.stop_after)
    app.run(port=arguments.port)
