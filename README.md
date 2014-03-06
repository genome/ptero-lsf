# PTero Shell Command Fork Service
[![Build Status](https://travis-ci.org/mark-burnett/ptero-shell-command-fork.png?branch=master)](https://travis-ci.org/mark-burnett/ptero-shell-command-fork)
[![Coverage Status](https://coveralls.io/repos/mark-burnett/ptero-shell-command-fork/badge.png)](https://coveralls.io/r/mark-burnett/ptero-shell-command-fork)

This project provides a way for the PTero workflow system to run shell commands
using [Celery](http://www.celeryproject.org/) via a REST API.

The API is currently described
[here](https://github.com/mark-burnett/ptero-apis/blob/master/shell-command-fork.md).


## Testing

To run tests:

    pip install tox
    tox
