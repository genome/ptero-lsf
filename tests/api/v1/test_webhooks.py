from .base import BaseAPITest
import pprint


class TestWebhooks(BaseAPITest):
    def test_scheduled_webhook(self):
        callback_server = self.create_callback_server([200])

        submit_data = {
            'command': 'true',
            'webhooks': {
                'scheduled': callback_server.url,
            },
        }
        self.update_submit_data(submit_data)

        post_response = self.post(self.jobs_url, submit_data)

        webhook_data = callback_server.stop()[0]

        self.assertIsInstance(webhook_data['lsfJobId'], int)
        self.assertEqual(webhook_data['statusHistory'][0]['status'], 'NEW')
        self.assertEqual(webhook_data['statusHistory'][1]['status'],
                'SUBMITTED')

    def test_success_webhook(self):
        callback_server = self.create_callback_server([200, 200])

        submit_data = {
            'command': 'true',
            'pollingInterval': 30,
            'webhooks': {
                'scheduled': callback_server.url,
                'succeeded': callback_server.url,
            },
        }
        self.update_submit_data(submit_data)

        post_response = self.post(self.jobs_url, submit_data)

        webhook_data = callback_server.stop()
        pprint.pprint(webhook_data)
        data = webhook_data[-1]

        self.assertIsInstance(data['lsfJobId'], int)
        self.assertEqual(data['statusHistory'][-1]['status'], 'SUCCEEDED')

    def test_failure_webhook(self):
        callback_server = self.create_callback_server([200, 200])

        submit_data = {
            'command': 'false',
            'pollingInterval': 30,
            'webhooks': {
                'scheduled': callback_server.url,
                'failed': callback_server.url,
            },
        }
        self.update_submit_data(submit_data)

        post_response = self.post(self.jobs_url, submit_data)

        webhook_data = callback_server.stop()
        pprint.pprint(webhook_data)
        data = webhook_data[-1]

        self.assertIsInstance(data['lsfJobId'], int)
        self.assertEqual(data['statusHistory'][-1]['status'], 'FAILED')

    def test_success_and_failure_webhook_with_success(self):
        callback_server = self.create_callback_server([200, 200])

        submit_data = {
            'command': 'true',
            'pollingInterval': 30,
            'webhooks': {
                'scheduled': callback_server.url,
                'succeeded': callback_server.url,
                'failed': callback_server.url,
            },
        }
        self.update_submit_data(submit_data)

        post_response = self.post(self.jobs_url, submit_data)

        webhook_data = callback_server.stop()
        pprint.pprint(webhook_data)
        data = webhook_data[-1]

        self.assertIsInstance(data['lsfJobId'], int)
        self.assertEqual(data['statusHistory'][-1]['status'], 'SUCCEEDED')

    def test_success_and_failure_webhook_with_failure(self):
        callback_server = self.create_callback_server([200, 200])

        submit_data = {
            'command': 'false',
            'pollingInterval': 30,
            'webhooks': {
                'scheduled': callback_server.url,
                'succeeded': callback_server.url,
                'failed': callback_server.url,
            },
        }
        self.update_submit_data(submit_data)

        post_response = self.post(self.jobs_url, submit_data)

        webhook_data = callback_server.stop()
        pprint.pprint(webhook_data)
        data = webhook_data[-1]

        self.assertIsInstance(data['lsfJobId'], int)
        self.assertEqual(data['statusHistory'][-1]['status'], 'FAILED')
