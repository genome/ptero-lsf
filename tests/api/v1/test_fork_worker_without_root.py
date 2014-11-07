from .base import BaseAPITest
import os
import unittest

@unittest.skipIf(os.environ.get('TEST_WITH_ROOT_WORKERS'),
    "running fork worker as root")
class TestForkWorkerRunningWithoutRoot(BaseAPITest):
    def test_user_of_job(self):
        callback_server = self.create_callback_server([200])

        user = 'nobody'
        post_response = self.post(self.jobs_url, {
            'commandLine': ['whoami'],
            'user': user,
            'callbacks': {
                'error': callback_server.url,
            },
        })

        webhook_data = callback_server.stop()
        expected_data = [
            {
                'status': 'error',
                'jobId': post_response.DATA['jobId'],
                'errorMessage': 'Failed to setreuid: Operation not permitted'
            }
        ]
        self.assertEqual(expected_data, webhook_data)
