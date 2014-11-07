from .base import BaseAPITest
import os
import unittest

@unittest.skipIf(os.environ.get('TEST_WITH_ROOT_WORKERS'),
    "running fork worker as root")
class TestForkWorkerRunningWithoutRoot(BaseAPITest):
    def test_user_of_job(self):
        callback_server = self.create_callback_server([200])

        user = 'nobody'
        self.post(self.jobs_url, {
            'commandLine': ['whoami'],
            'user': user,
            'callbacks': {
                'error': callback_server.url,
            },
        })

        webhook_data = callback_server.stop()
        self.assertEqual('error', webhook_data[0]['status'])
        self.assertEqual('Failed to setreuid: Operation not permitted', webhook_data[0]['errorMessage'])
