from .base import BaseAPITest
import os
import re
import unittest

@unittest.skipIf(not os.environ.get('TEST_WITH_ROOT_WORKERS'),
    "not running fork worker as root")
class TestForkWorkerRunningAsRoot(BaseAPITest):
    def test_job_user_and_group(self):
        callback_server = self.create_callback_server([200])

        username = 'nobody'
        primarygroup = 'nobody'
        self.post(self.jobs_url, {
            'commandLine': ['id'],
            'username': username,
            'callbacks': {
                'ended': callback_server.url,
            },
        })

        webhook_data = callback_server.stop()
        id_result = webhook_data[0]['stdout']

        actual_username = self._find_match(r"uid=\d+\((\w+)\)", id_result)
        actual_primarygroup = self._find_match(r"gid=\d+\((\w+)\)", id_result)

        self.assertEqual(username, actual_username)
        self.assertEqual(primarygroup, actual_username)

    def _find_match(self, regexp, target):
        match = re.search(regexp, target)
        if match:
            return match.group(1)
        else:
            return ''
