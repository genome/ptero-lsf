from .base import BaseAPITest
import simplejson


class TestJobStatus(BaseAPITest):
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
