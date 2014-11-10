from .base import BaseAPITest
import os
import platform
import simplejson
import tempfile


class TestCwd(BaseAPITest):
    def setUp(self):
        super(TestCwd, self).setUp()

        if platform.system() == 'Darwin':
            self.job_working_directory = tempfile.mkdtemp(dir='/private/tmp')
        else:
            self.job_working_directory = tempfile.mkdtemp()

    def tearDown(self):
        super(TestCwd, self).tearDown()
        os.rmdir( self.job_working_directory )

    def test_job_working_directory(self):
        callback_server = self.create_callback_server([200])

        post_data = {
            'commandLine': ['/bin/pwd'],
            'user': self.job_user,
            'workingDirectory': self.job_working_directory,
            'callbacks': {
                'ended': callback_server.url,
            },
        }

        self.post(self.jobs_url, post_data)

        webhook_data = callback_server.stop()
        actual_working_directory = webhook_data[0]['stdout'].strip('\n')
        self.assertEqual(self.job_working_directory, actual_working_directory)

    def test_job_working_directory_does_not_exist(self):
        callback_server = self.create_callback_server([200])

        post_data = {
            'commandLine': ['/bin/pwd'],
            'user': self.job_user,
            'workingDirectory': '/does/not/exist',
            'callbacks': {
                'error': callback_server.url,
            },
        }

        post_response = self.post(self.jobs_url, post_data)
        webhook_data = callback_server.stop()
        expected_data = [
            {
                'status': 'error',
                'jobId': post_response.DATA['jobId'],
                'errorMessage': 'chdir(/does/not/exist): No such file or directory'
            },
        ]
        self.assertEqual(webhook_data, expected_data)

    def test_job_working_directory_access_denied(self):
        callback_server = self.create_callback_server([200])

        os.chmod(self.job_working_directory, 0)
        post_data = {
            'commandLine': ['/bin/pwd'],
            'user': self.job_user,
            'workingDirectory': self.job_working_directory,
            'callbacks': {
                'error': callback_server.url,
            },
        }

        post_response = self.post(self.jobs_url, post_data)
        webhook_data = callback_server.stop()
        expected_data = [
            {
                'status': 'error',
                'jobId': post_response.DATA['jobId'],
                'errorMessage': 'chdir(%s): Permission denied' % self.job_working_directory
            },
        ]
        self.assertEqual(webhook_data, expected_data)
