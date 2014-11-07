from .base import BaseAPITest
import simplejson


class TestJobStatus(BaseAPITest):
    def test_successful_job_has_succeeded_status(self):
        callback_server = self.create_callback_server([200])

        post_response = self.post(self.jobs_url, {
            'commandLine': ['true'],
            'user': self.job_user,
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
            'user': self.job_user,
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
            'user': self.job_user,
            'callbacks': {
                'begun': callback_server.url,
            },
        })

        callback_server.stop()

        get_response = self.get(post_response.headers['Location'])
        self.assertEqual('running', get_response.DATA['status'])
