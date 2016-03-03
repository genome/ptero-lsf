from . import validators
from flask import g, request, url_for
from flask.ext.restful import Resource
from ptero_common import nicer_logging
from ptero_common.nicer_logging import logged_response
from ptero_common.exceptions import NoSuchEntityError
from ptero_common.view_wrapper import handles_no_such_entity_error
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
    @handles_no_such_entity_error
    def get(self, pk):
        job_data = g.backend.get_job(pk)
        return job_data, 200

    @logged_response(logger=LOG)
    @handles_no_such_entity_error
    def delete(self, pk):
        g.backend.delete_job(pk)
        return {"message": "Job %s was deleted" % pk}, 200

    @logged_response(logger=LOG)
    def put(self, pk):
        LOG.info("Handling POST request to %s from %s for job (%s)",
                request.url, request.access_route[0], pk,
                extra={'jobId': pk})
        return _submit_job(job_id=pk)

    @logged_response(logger=LOG)
    @handles_no_such_entity_error
    def patch(self, pk):
        LOG.info("Handling PATCH request to %s from %s for job (%s)",
                request.url, request.access_route[0], pk,
                extra={'jobId': pk})

        data = request.json
        patch_keys = set(data.keys())
        allowed_keys = set(['status', 'stdout', 'stderr'])

        disallowed_keys = patch_keys - allowed_keys
        if disallowed_keys:
            return {"error": "Not allowing PATCH of %s" %
                    str(list(disallowed_keys))}, 400

        try:
            job_data = g.backend.update_job(pk, **data)
            return job_data, 200
        except NoSuchEntityError:
            raise
        except:
            LOG.exception("Exception while updating job (%s)", pk,
                    extra={'jobId': pk})
            return {"error": "Could not update job"}, 400


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


class ServerInfo(Resource):
    @logged_response(logger=LOG)
    def get(self):
        return g.backend.server_info(), 200
