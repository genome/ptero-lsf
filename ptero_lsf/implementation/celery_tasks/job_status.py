from .. import models
from sqlalchemy import func
import celery
import lsf

__all__ = ['UpdateJobStatus']


class UpdateJobStatus(celery.Task):
    def run(self, job_id):
        session = celery.current_app.Session()
        service_job = session.query(models.Job).get(job_id)

        if service_job.lsf_job_id is None:
            service_job.set_status('ERRORED')

        else:
            lsf_job = lsf.get_job(service_job.lsf_job_id)

            job_data = lsf_job.as_dict

            service_job.update_status(job_data['statuses'])

        session.commit()
