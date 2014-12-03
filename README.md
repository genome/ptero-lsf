# PTero LSF Service
[![Requirements Status](https://requires.io/github/genome/ptero-lsf/requirements.svg?branch=master)](https://requires.io/github/genome/ptero-lsf/requirements/?branch=master)

This project provides a way for the PTero workflow system to run commands via
LSF using [Celery](http://www.celeryproject.org/) via a REST API.

The API is currently described
[here](https://github.com/genome/ptero-apis/blob/master/lsf.md).


## Testing

To run tests:

    pip install tox
    tox


## Development

To launch a development server:

    pip install -r requirements.txt
    pip install honcho
    honcho start -f Procfile.dev -c worker=4

You can then connect to the webserver at http://localhost:7200
