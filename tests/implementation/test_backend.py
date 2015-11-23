from pprint import pformat
from ptero_common import statuses
from ptero_lsf.implementation import Factory
from ptero_lsf.implementation import models
import os
import pwd
import time
import unittest
import uuid


class TestBackend(unittest.TestCase):

    def setUp(self):
        self.factory = Factory(database_url=os.environ['PTERO_LSF_DB_STRING'])
        self.backend = self.factory.create_backend()

    @property
    def session(self):
        return self.backend.session

    def test_update_invalid_job(self):
        job_id = str(uuid.uuid4())
        self.backend.create_job('false', job_id, user='nobody')
        job = self.session.query(models.Job).get(job_id)
        job.lsf_job_id = 82
        self.assertFalse(self.backend.update_job_status(job_id))

    def test_update_job_without_lsf_id(self):
        job_id = str(uuid.uuid4())
        self.backend.create_job('false', job_id, user='nobody')
        job = self.session.query(models.Job).get(job_id)
        job.lsf_job_id = None
        self.assertFalse(self.backend.update_job_status(job_id))

    def test_create_and_cancel_job(self):
        job_id = str(uuid.uuid4())
        user = pwd.getpwuid(os.getuid())[0]
        print "creating job %s" % job_id
        self.backend.create_job('sleep 60', job_id, user=user)

        # this should cancel it before it gets dispatched to lsf
        self.assertFalse(self.backend.job_is_canceled(job_id))
        print "canceling job %s" % job_id
        self.backend.cancel_job(job_id, 'Canceled by test')
        self.assertTrue(self.backend.job_is_canceled(job_id))

        for i in range(20):
            if self.backend.update_job_status(job_id):
                print "job %s has dispatched to lsf" % job_id
                break
            else:
                print "Waiting for job %s to dispatch to lsf" % job_id
                time.sleep(1)

        # the job should be dispatched to lsf and then killed leaving it in a
        # 'failed' status.
        job_data = self.backend.get_job(job_id)
        print "job %s: %s" % (job_id, pformat(job_data))
        self.assertEqual(self.backend.get_job(job_id)['status'],
                statuses.failed)
