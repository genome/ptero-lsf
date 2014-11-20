# PTero Shell Command Service
[![Build Status](https://travis-ci.org/genome/ptero-shell-command.png?branch=master)](https://travis-ci.org/genome/ptero-shell-command)
[![Coverage Status](https://coveralls.io/repos/genome/ptero-shell-command/badge.png)](https://coveralls.io/r/genome/ptero-shell-command)

This project provides a way for the PTero workflow system to run shell commands
using [Celery](http://www.celeryproject.org/) via a REST API.

The API is currently described
[here](https://github.com/genome/ptero-apis/blob/master/shell-command.md).


## Testing

To run tests:

    pip install tox
    tox


## Development

To launch a development server:

    pip install -r requirements.txt
    pip install honcho
    honcho start -f Procfile.dev -c worker=4

You can then connect to the webserver at http://localhost:5200
