from .base import BaseAPITest
import lsf
import time


class DeleteTest(BaseAPITest):
    def test_deleting_job_after_scheduled(self):
        cb_server = self.create_callback_server([200])

        submit_data = {
            'command': 'sleep 8675309',
            'pollingInterval': 3,
            'options': {
                'numProcessors': 1,
            },
            'rLimits': {
                'RSS': 1000000,
            },
            'webhooks': {
                'submitted': cb_server.url,
            },
        }
        self.update_submit_data(submit_data)

        print "Posting job %s" % self.jobs_url
        response = self.post(self.jobs_url, submit_data)
        job_url = response.headers['Location']

        self.assertIn('jobId', response.DATA)
        self.assertEqual(response.status_code, 201)

        print "Awaiting submitted webhook"
        cb_server.stop()

        get_response = self.get(job_url)

        lsf_job_id = get_response.DATA['lsfJobId']

        def job_is_running():
            return self.lsf_job_is_running(lsf_job_id)
        self._retry_until_true(job_is_running, 20, 1)

        print "Deleting job %s" % job_url
        delete_response = self.delete(job_url)
        self.assertEqual(delete_response.status_code, 200)

        def job_is_not_running():
            return not self.lsf_job_is_running(lsf_job_id)
        self._retry_until_true(job_is_not_running, 20, 1)

    def _retry_until_true(self, func, timeout, delay):
        start_time = time.time()
        while True:
            try:
                if func():
                    return
            except:
                pass

            if (time.time() - start_time) >= timeout:
                raise RuntimeError("Timeout exceeded")
            else:
                time.sleep(delay)

    @staticmethod
    def lsf_job_is_running(lsf_job_id):
        print "Checking on LSF job (%s)" % lsf_job_id
        lsf_job = lsf.get_job(lsf_job_id)

        job_data = lsf_job.as_dict
        statuses = job_data['statuses']
        result = 'RUN' in statuses

        print "LSF job (%s) is %srunning" % (lsf_job_id,
                '' if result else 'not ')
        return result
