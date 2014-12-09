from .. import models
import celery

__all__ = ['LSFTask']


class LSFTask(celery.Task):
    def run(self, job_id):
        session = celery.current_app.Session()
        service_job = session.query(models.Job).get(job_id)

        try:
            lsf_job = _submit_job(service_job)

            service_job.lsf_job_id = lsf_job.job_id
            service_job.set_status('SUBMITTED')

        except:
            service_job.set_status('ERRORED')

        session.commit()


def _submit_job(service_job):
    return service_job.submit()
