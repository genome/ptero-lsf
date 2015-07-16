from .. import models
from ptero_lsf.implementation import statuses
import celery
import lsf

__all__ = ['UpdateJobStatus']


class UpdateJobStatus(celery.Task):
    def run(self, job_id):
        backend = celery.current_app.factory.create_backend()
        session = backend.session
        service_job = session.query(models.Job).get(job_id)

        if service_job.lsf_job_id is None:
            service_job.set_status(statuses.errored,
                    message='LSF job id for job %s is None' % job_id)

        else:
            lsf_job = lsf.get_job(service_job.lsf_job_id)

            job_data = lsf_job.as_dict

            service_job.update_status(job_data['statuses'])

        session.commit()
