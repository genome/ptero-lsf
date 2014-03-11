from .base import DeferredAPITest
import time


class JobStatusTest(DeferredAPITest):
    def test_successful_job_has_succeeded_status(self):
        self.start_worker()

        post_response = self.post('/v1/jobs',
                {'command_line': ['/usr/bin/true']})
        time.sleep(5)

        get_response = self.get(post_response.headers['Location'])
        self.assertEqual('succeeded', get_response.DATA['status'])
