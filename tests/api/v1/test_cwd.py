from .base import BaseAPITest
import os
import platform
import tempfile
import simplejson


class TestCwd(BaseAPITest):
    def setUp(self):
        super(TestCwd, self).setUp()

        if platform.system() == 'Darwin':
            self.job_cwd = tempfile.mkdtemp(dir='/private/tmp')
        else:
            self.job_cwd = tempfile.mkdtemp()

    def tearDown(self):
        super(TestCwd, self).tearDown()
        os.rmdir( self.job_cwd )

    def test_cwd(self):
        callback_server = self.create_callback_server([200])
        
        post_data = {
            'commandLine': ['/bin/pwd'],
            'username': self.job_username,
            'cwd': self.job_cwd,
            'callbacks': {
                'ended': callback_server.url,
            },
        }
        
        self.post(self.jobs_url, post_data)
        
        webhook_data = callback_server.stop()
        actual_cwd = webhook_data[0]['stdout'].strip('\n')
        self.assertEqual(self.job_cwd, actual_cwd)
