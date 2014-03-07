from . import parsers
from flask import g, request, url_for
from flask.ext.restful import Resource, marshal
from ptero_shell_command_fork import exceptions


class JobListView(Resource):
    def post(self):
        data = parsers.get_job_post_data()
        job_id = g.backend.create_job(**data)
        return {}, 201, {'Location': url_for('job', pk=job_id)}


class JobView(Resource):
    def get(self, pk):
        return {'status': 'succeeded'}
