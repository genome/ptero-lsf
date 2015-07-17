from ptero_lsf.implementation import Factory
from ptero_lsf.implementation import models
import os
import unittest


class TestBackend(unittest.TestCase):

    def setUp(self):
        self.factory = Factory(
            database_url=os.environ.get('PTERO_LSF_DB_STRING', 'sqlite://'))
        self.backend = self.factory.create_backend()

    @property
    def session(self):
        return self.backend.session

    def test_update_invalid_job(self):
        job_id, job_dict = self.backend.create_job('false', user='nobody')
        job = self.session.query(models.Job).get(job_id)
        job.lsf_job_id = 82
        self.assertFalse(self.backend.update_job_status(job_id))

    def test_update_job_without_lsf_id(self):
        job_id, job_dict = self.backend.create_job('false', user='nobody')
        job = self.session.query(models.Job).get(job_id)
        job.lsf_job_id = None
        self.assertFalse(self.backend.update_job_status(job_id))
