from .base import BaseAPITest
import simplejson


class TestJobStatus(BaseAPITest):
    def test_successful_job_has_succeeded_status(self):
        callback_server = self.create_callback_server([200])

        post_response = self.post(self.jobs_url, {
            'commandLine': ['true'],
            'username': self.job_username,
            'callbacks': {
                'ended': callback_server.url,
            },
        })

        callback_server.stop()

        get_response = self.get(post_response.headers['Location'])
        self.assertEqual('succeeded', get_response.DATA['status'])

    def test_failed_job_has_failed_status(self):
        callback_server = self.create_callback_server([200])

        post_response = self.post(self.jobs_url, {
            'commandLine': ['false'],
            'username': self.job_username,
            'callbacks': {
                'ended': callback_server.url,
            },
        })

        callback_server.stop()

        get_response = self.get(post_response.headers['Location'])
        self.assertEqual('failed', get_response.DATA['status'])

    def test_running_job_has_running_status(self):
        callback_server = self.create_callback_server([200])

        post_response = self.post(self.jobs_url, {
            'commandLine': ['sleep', '10'],
            'username': self.job_username,
            'callbacks': {
                'begun': callback_server.url,
            },
        })

        callback_server.stop()

        get_response = self.get(post_response.headers['Location'])
        self.assertEqual('running', get_response.DATA['status'])
