from .base import BaseAPITest
import os
import unittest

@unittest.skipIf(not os.environ.get('TEST_WITH_ROOT_WORKERS'),
    "not running fork worker as root")
class TestForkWorkerRunningAsRoot(BaseAPITest):
    def test_user_of_job(self):
        callback_server = self.create_callback_server([200])

        username = 'nobody'
        self.post(self.jobs_url, {
            'commandLine': ['whoami'],
            'username': username,
            'callbacks': {
                'ended': callback_server.url,
            },
        })

        webhook_data = callback_server.stop()
        actual_username = webhook_data[0]['stdout'].rstrip('\n')

        self.assertEqual(username, actual_username)
