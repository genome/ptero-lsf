from . import validators
from flask import g, request, url_for
from flask.ext.restful import Resource
from ptero_common import nicer_logging
from ptero_common.nicer_logging import logged_response
import uuid


LOG = nicer_logging.getLogger(__name__)


class JobListView(Resource):
    @logged_response(logger=LOG)
    def post(self):
        job_id = str(uuid.uuid4())
        LOG.info("Handling POST request to %s from %s for job (%s)",
                request.url, request.access_route[0], job_id,
                extra={'jobId': job_id})
        return _submit_job(job_id=job_id)


class JobView(Resource):
    @logged_response(logger=LOG)
    def get(self, pk):
        job_data = g.backend.get_job(pk)
        if job_data:
            return job_data, 200
        else:
            return None, 404

    @logged_response(logger=LOG)
    def put(self, pk):
        LOG.info("Handling POST request to %s from %s for job (%s)",
                request.url, request.access_route[0], pk,
                extra={'jobId': pk})
        return _submit_job(job_id=pk)


def _submit_job(job_id):
    try:
        LOG.debug("Validating JSON body of request for job (%s)", job_id,
            extra={'jobId': job_id})
        data = validators.get_job_post_data()
    except Exception as e:
        LOG.exception("Exception occured while validating JSON body of"
            " request to %s from %s for job (%s)", request.url,
            request.access_route[0], job_id,
            extra={'jobId': job_id})
        LOG.info("Returning 400 in response to request for job (%s)",
                job_id, extra={'jobId': job_id})
        return {'error': e.message}, 400

    data['job_id'] = job_id
    g.backend.create_job(**data)

    LOG.info("Returning 201 in response to request for job (%s)",
            job_id, extra={'jobId': job_id})
    return {'jobId': job_id}, 201, {'Location': url_for('.job', pk=job_id,
        _external=True)}
