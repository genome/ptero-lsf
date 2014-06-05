from ..base import BaseAPITest
import simplejson


class TestMockWebserver(BaseAPITest):
    def test_mock_webserver_works(self):
        self.start_webserver([302])
        import requests
        request_body = {"bob": "hi im your friend"}
        response = requests.put(self.webhook_url,
                simplejson.dumps(request_body))
        self.assertEqual(302, response.status_code)

        datas = self.stop_webserver()
        self.assertEqual(request_body, datas[0])


class TestWebhooks(BaseAPITest):
    def test_begun_webhook(self):
        self.start_webserver([200])

        post_response = self.post(self.jobs_url, {
            'command_line': ['true'],
            'callbacks': {
                'begun': self.webhook_url,
            },
        })

        webhook_data = self.stop_webserver()
        expected_data = [
            {
                'status': 'begun',
                'job_id': post_response.DATA['job_id'],
            },
        ]
        self.assertEqual(expected_data, webhook_data)

    def test_succeeded_webhook(self):
        self.start_webserver([200])

        post_response = self.post(self.jobs_url, {
            'command_line': ['true'],
            'callbacks': {
                'ended': self.webhook_url,
            },
        })

        webhook_data = self.stop_webserver()
        expected_data = [
            {
                'status': 'ended',
                'exit_code': 0,
                'stdout': '',
                'stderr': '',
                'job_id': post_response.DATA['job_id'],
            },
        ]
        self.assertEqual(expected_data, webhook_data)

    def test_failed_webhook(self):
        self.start_webserver([200])

        post_response = self.post(self.jobs_url, {
            'command_line': ['false'],
            'callbacks': {
                'ended': self.webhook_url,
            },
        })

        webhook_data = self.stop_webserver()
        expected_data = [
            {
                'status': 'ended',
                'exit_code': 1,
                'stdout': '',
                'stderr': '',
                'job_id': post_response.DATA['job_id'],
            },
        ]
        self.assertEqual(expected_data, webhook_data)

    def test_multiple_webhooks(self):
        self.start_webserver([200, 200])

        post_response = self.post(self.jobs_url, {
            'command_line': ['true'],
            'callbacks': {
                'begun': self.webhook_url,
                'ended': self.webhook_url,
            },
        })

        webhook_data = self.stop_webserver()
        expected_data = [
            {
                'status': 'begun',
                'job_id': post_response.DATA['job_id'],
            },
            {
                'status': 'ended',
                'exit_code': 0,
                'stdout': '',
                'stderr': '',
                'job_id': post_response.DATA['job_id'],
            },
        ]
        self.assertEqual(expected_data, webhook_data)

    def test_environment_set_for_job(self):
        self.start_webserver([200])
        environment = {
            'FOO': 'bar',
        }

        post_data = {
            'command_line': ['/usr/bin/env'],
            'environment': environment,
            'callbacks': {
                'ended': self.webhook_url,
            },
        }

        self.post(self.jobs_url, post_data)

        webhook_data = self.stop_webserver()

        stdout = webhook_data[0]['stdout']
        actual_environment = _extract_environment_dict(stdout)

        self.assertEqual(environment, actual_environment)

    def test_stdin_stdout_pass_through(self):
        self.start_webserver([200])
        stdin = 'this is just some text'

        post_data = {
            'command_line': ['cat'],
            'stdin': stdin,
            'callbacks': {
                'ended': self.webhook_url,
            },
        }

        self.post(self.jobs_url, post_data)

        webhook_data = self.stop_webserver()
        self.assertEqual(stdin, webhook_data[0]['stdout'])


class JobStatusTest(BaseAPITest):
    def test_successful_job_has_succeeded_status(self):
        self.start_webserver([200])

        post_response = self.post(self.jobs_url, {
            'command_line': ['true'],
            'callbacks': {
                'ended': self.webhook_url,
            },
        })

        self.stop_webserver()

        get_response = self.get(post_response.headers['Location'])
        self.assertEqual('succeeded', get_response.DATA['status'])

    def test_failed_job_has_failed_status(self):
        self.start_webserver([200])

        post_response = self.post(self.jobs_url, {
            'command_line': ['false'],
            'callbacks': {
                'ended': self.webhook_url,
            },
        })

        self.stop_webserver()

        get_response = self.get(post_response.headers['Location'])
        self.assertEqual('failed', get_response.DATA['status'])

    def test_running_job_has_running_status(self):
        self.start_webserver([200])

        post_response = self.post(self.jobs_url, {
            'command_line': ['sleep', '10'],
            'callbacks': {
                'begun': self.webhook_url,
            },
        })

        self.stop_webserver()

        get_response = self.get(post_response.headers['Location'])
        self.assertEqual('running', get_response.DATA['status'])


def _extract_environment_dict(stdin):
    result = {}
    for line in stdin.split('\n'):
        if line:
            key, value = line.split('=')
            result[key] = value.strip('\n')
    return result
