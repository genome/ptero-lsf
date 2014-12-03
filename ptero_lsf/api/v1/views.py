from . import validators
from flask import g, request
from flask.ext.restful import Resource


class JobListView(Resource):
    def post(self):
        try:
            data = validators.get_job_post_data()
        except Exception as e:
            return {'error': e.message}, 400

        job_id = g.backend.create_job(**data)
        return {'jobId': job_id}, 201
