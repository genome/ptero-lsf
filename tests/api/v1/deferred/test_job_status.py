from ...base import BaseAPITest
import time


class JobStatusTest(BaseAPITest):
    def test_successful_job_has_succeeded_status(self):
        post_response = self.post(self.jobs_url,
                {'command_line': ['true']})
        time.sleep(5)

        get_response = self.get(post_response.headers['Location'])
        self.assertEqual('succeeded', get_response.DATA['status'])

    def test_failed_job_has_failed_status(self):
        post_response = self.post(self.jobs_url,
                {'command_line': ['false']})
        time.sleep(5)

        get_response = self.get(post_response.headers['Location'])
        self.assertEqual('failed', get_response.DATA['status'])

    def test_running_job_has_running_status(self):
        post_response = self.post(self.jobs_url,
                {'command_line': ['sleep', '10']})
        time.sleep(2)

        get_response = self.get(post_response.headers['Location'])
        self.assertEqual('running', get_response.DATA['status'])
