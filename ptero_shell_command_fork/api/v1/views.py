from flask import g, request, url_for
from flask.ext.restful import Resource, marshal
from ptero_shell_command_fork import exceptions


class JobListView(Resource):
    def post(self):
        return {}


class JobView(Resource):
    def get(self, pk):
        return {}
