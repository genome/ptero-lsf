from .base import BaseAPITest
import pprint


class TestWebhooks(BaseAPITest):
    def test_submitted_webhook(self):
        callback_server = self.create_callback_server([200])

        submit_data = {
            'command': 'true',
            'webhooks': {
                'submitted': callback_server.url,
            },
        }
        self.update_submit_data(submit_data)

        self.post(self.jobs_url, submit_data)

        webhook_data = callback_server.stop()[0]
        print pprint.pformat(webhook_data)

        self.assertIsInstance(webhook_data['lsfJobId'], int)
        self.assertIn('jobId', webhook_data)
        self.assertEqual(webhook_data['statusHistory'][0]['status'], 'new')
        self.assertEqual(webhook_data['statusHistory'][1]['status'],
            'submitted')

    def test_success_and_failure_webhook_with_success(self):
        callback_server = self.create_callback_server([200])

        submit_data = {
            'command': 'true',
            'pollingInterval': 30,
            'webhooks': {
                'succeeded': callback_server.url,
                'failed': callback_server.url,
            },
        }
        self.update_submit_data(submit_data)

        self.post(self.jobs_url, submit_data)

        webhook_data = callback_server.stop()
        pprint.pprint(webhook_data)
        data = webhook_data[-1]

        self.assertIsInstance(data['lsfJobId'], int)
        self.assertIn('jobId', data)
        self.assertEqual(data['statusHistory'][-1]['status'], 'succeeded')

    def test_success_and_failure_webhook_with_failure(self):
        callback_server = self.create_callback_server([200])

        submit_data = {
            'command': 'false',
            'pollingInterval': 30,
            'webhooks': {
                'succeeded': callback_server.url,
                'failed': callback_server.url,
            },
        }
        self.update_submit_data(submit_data)

        self.post(self.jobs_url, submit_data)

        webhook_data = callback_server.stop()
        pprint.pprint(webhook_data)
        data = webhook_data[-1]

        self.assertIsInstance(data['lsfJobId'], int)
        self.assertIn('jobId', data)
        self.assertEqual(data['statusHistory'][-1]['status'], 'failed')

    def test_multiple_callbacks(self):
        callback_server = self.create_callback_server([200, 200])

        submit_data = {
            'command': 'true',
            'pollingInterval': 30,
            'webhooks': {
                'succeeded': [callback_server.url, callback_server.url],
            },
        }
        self.update_submit_data(submit_data)

        self.post(self.jobs_url, submit_data)

        webhook_data = callback_server.stop()
        pprint.pprint(webhook_data)
        data = webhook_data[-1]

        self.assertIsInstance(data['lsfJobId'], int)
        self.assertIn('jobId', data)
        self.assertEqual(data['statusHistory'][-1]['status'], 'succeeded')
