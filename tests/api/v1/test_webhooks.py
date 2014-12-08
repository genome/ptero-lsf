from .base import BaseAPITest


class TestWebhooks(BaseAPITest):
    def test_submit_webhook(self):
        callback_server = self.create_callback_server([200])

        post_response = self.post(self.jobs_url, {
            'command': 'true',
            'webhooks': {
                'submit': callback_server.url,
            },
        })

        webhook_data = callback_server.stop()[0]

        self.assertIsInstance(webhook_data['lsfJobId'], int)
        self.assertEqual(webhook_data['statusHistory'][0]['status'], 'NEW')
        self.assertEqual(webhook_data['statusHistory'][1]['status'],
                'SUBMITTED')
