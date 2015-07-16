import celery

__all__ = ['UpdateJobStatus']


class UpdateJobStatus(celery.Task):
    def run(self, job_id):
        backend = celery.current_app.factory.create_backend()
        backend.update_job_status(job_id)
