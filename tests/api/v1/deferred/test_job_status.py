from .base import DeferredAPITest
import time


class JobStatusTest(DeferredAPITest):
    def test_successful_job_has_succeeded_status(self):
        self.start_worker()

        post_response = self.post('/v1/jobs',
                {'command_line': ['true']})
        self.wait()

        get_response = self.get(post_response.headers['Location'])
        self.assertEqual('succeeded', get_response.DATA['status'])

    def test_failed_job_has_failed_status(self):
        self.start_worker()

        post_response = self.post('/v1/jobs',
                {'command_line': ['false']})
        self.wait()

        get_response = self.get(post_response.headers['Location'])
        self.assertEqual('failed', get_response.DATA['status'])

    def test_running_job_has_running_status(self):
        self.start_worker()
        self.wait()

        post_response = self.post('/v1/jobs',
                {'command_line': ['sleep', '30']})
        time.sleep(2)

        get_response = self.get(post_response.headers['Location'])
        self.assertEqual('running', get_response.DATA['status'])
