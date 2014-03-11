#!/usr/bin/env python

import argparse
from flask import Flask, request


_RESPONSE_CODES = []
def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('response_codes', nargs='+', type=int)

    arguments = parser.parse_args()

    global _RESPONSE_CODES
    _RESPONSE_CODES = list(reversed(arguments.response_codes))

def next_response_code():
    return _RESPONSE_CODES.pop()

app = Flask(__name__)


@app.route('/', methods=['PUT'])
def log_request():
    print request.data
    return '', next_response_code()


if __name__ == '__main__':
    parse_arguments()
    app.run(port=5112)
