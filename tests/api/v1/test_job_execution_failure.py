from .base import BaseAPITest
import os
import unittest

class TestJobExecutionFailure(BaseAPITest):
    def test_exception_on_setuid_failure(self):
        callback_server = self.create_callback_server([200])

        user = '_no_such_user'
        post_response = self.post(self.jobs_url, {
            'commandLine': ['true'],
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
                'errorMessage': 'getpwnam(): name not found: _no_such_user'
            }
        ]
        self.assertEqual(expected_data, webhook_data)
