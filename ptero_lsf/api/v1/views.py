from . import parsers
from flask import g, request, url_for
from flask.ext.restful import Resource, marshal
from ptero_lsf import exceptions


class JobListView(Resource):
    def post(self):
        data = parsers.get_job_post_data()
        job_id = g.backend.create_job(**data)
        return {'jobId': job_id}, 201
