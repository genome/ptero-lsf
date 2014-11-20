from .base import BaseAPITest
import simplejson


class TestWebhooks(BaseAPITest):
    def test_begun_webhook(self):
        callback_server = self.create_callback_server([200])

        post_response = self.post(self.jobs_url, {
            'commandLine': ['true'],
            'user': self.job_user,
            'workingDirectory': self.job_working_directory,
            'callbacks': {
                'begun': callback_server.url,
            },
        })

        webhook_data = callback_server.stop()
        expected_data = [
            {
                'status': 'begun',
                'jobId': post_response.DATA['jobId'],
            },
        ]
        self.assertEqual(expected_data, webhook_data)

    def test_succeeded_webhook(self):
        callback_server = self.create_callback_server([200])

        post_response = self.post(self.jobs_url, {
            'commandLine': ['true'],
            'user': self.job_user,
            'workingDirectory': self.job_working_directory,
            'callbacks': {
                'ended': callback_server.url,
            },
        })

        webhook_data = callback_server.stop()
        expected_data = [
            {
                'status': 'ended',
                'exitCode': 0,
                'stdout': '',
                'stderr': '',
                'jobId': post_response.DATA['jobId'],
            },
        ]
        self.assertEqual(expected_data, webhook_data)

    def test_failed_webhook(self):
        callback_server = self.create_callback_server([200])

        post_response = self.post(self.jobs_url, {
            'commandLine': ['false'],
            'user': self.job_user,
            'workingDirectory': self.job_working_directory,
            'callbacks': {
                'ended': callback_server.url,
            },
        })

        webhook_data = callback_server.stop()
        expected_data = [
            {
                'status': 'ended',
                'exitCode': 1,
                'stdout': '',
                'stderr': '',
                'jobId': post_response.DATA['jobId'],
            },
        ]
        self.assertEqual(expected_data, webhook_data)

    def test_multiple_webhooks(self):
        callback_server = self.create_callback_server([200, 200])

        post_response = self.post(self.jobs_url, {
            'commandLine': ['true'],
            'user': self.job_user,
            'workingDirectory': self.job_working_directory,
            'callbacks': {
                'begun': callback_server.url,
                'ended': callback_server.url,
            },
        })

        webhook_data = callback_server.stop()
        expected_data = [
            {
                'status': 'begun',
                'jobId': post_response.DATA['jobId'],
            },
            {
                'status': 'ended',
                'exitCode': 0,
                'stdout': '',
                'stderr': '',
                'jobId': post_response.DATA['jobId'],
            },
        ]
        self.assertEqual(expected_data, webhook_data)

    def test_environment_set_for_job(self):
        callback_server = self.create_callback_server([200])
        environment = {
            'FOO': 'bar',
        }

        post_data = {
            'commandLine': ['/usr/bin/env'],
            'user': self.job_user,
            'workingDirectory': self.job_working_directory,
            'environment': environment,
            'callbacks': {
                'ended': callback_server.url,
            },
        }

        self.post(self.jobs_url, post_data)

        webhook_data = callback_server.stop()

        stdout = webhook_data[0]['stdout']
        actual_environment = _extract_environment_dict(stdout)

        self.assertEqual(environment, actual_environment)

    def test_stdin_stdout_pass_through(self):
        callback_server = self.create_callback_server([200])
        stdin = 'this is just some text'

        post_data = {
            'commandLine': ['cat'],
            'user': self.job_user,
            'workingDirectory': self.job_working_directory,
            'stdin': stdin,
            'callbacks': {
                'ended': callback_server.url,
            },
        }

        self.post(self.jobs_url, post_data)

        webhook_data = callback_server.stop()
        self.assertEqual(stdin, webhook_data[0]['stdout'])

    def test_command_not_found(self):
        callback_server = self.create_callback_server([200])

        post_response = self.post(self.jobs_url, {
            'commandLine': ['bad-command'],
            'user': self.job_user,
            'workingDirectory': self.job_working_directory,
            'callbacks': {
                'error': callback_server.url,
            },
        })

        webhook_data = callback_server.stop()
        expected_data = [
            {
                'status': 'error',
                'errorMessage': 'Command not found: bad-command',
                'jobId': post_response.DATA['jobId'],
            },
        ]
        self.assertEqual(expected_data, webhook_data)


def _extract_environment_dict(stdin):
    result = {}
    for line in stdin.split('\n'):
        if line:
            key, value = line.split('=')
            result[key] = value.strip('\n')
    return result
