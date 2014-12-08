from .. import models
from sqlalchemy import func
import celery
import lsf

__all__ = ['UpdateJobStatus']


class UpdateJobStatus(celery.Task):
    def run(self, job_id):
        session = celery.current_app.Session()
        service_job = session.query(models.Job).get(job_id)

        lsf_job = lsf.get_job(service_job.lsf_job_id)

        job_data = lsf_job.as_dict

        webhook_to_trigger = service_job.update_status(job_data['statuses'])
        service_job.update_poll_after()
        service_job.trigger_webhook(webhook_to_trigger)
        session.commit()
