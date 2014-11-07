from .base import BaseAPITest
import os
import unittest

class TestJobExecutionFailure(BaseAPITest):
    def test_exception_on_setuid_failure(self):
        callback_server = self.create_callback_server([200])

        user = '_no_such_user'
        self.post(self.jobs_url, {
            'commandLine': ['true'],
            'user': user,
            'callbacks': {
                'error': callback_server.url,
            },
        })

        webhook_data = callback_server.stop()
        actual_status = webhook_data[0]['status']

        self.assertEqual('error', actual_status)
