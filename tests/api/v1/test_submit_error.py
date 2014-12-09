from .base import BaseAPITest
import pprint


class TestSubmitBadRequestShouldReturn400(BaseAPITest):
    def submit_should_return_400(self, data):
        response = self.post(self.jobs_url, data)
        self.assertEqual(400, response.status_code)

    def test_empty_requeset(self):
        self.submit_should_return_400({})

    def test_missing_command(self):
        self.submit_should_return_400({
            'options': {'outFile': '/some/output/path'}
        })

    def test_empty_command(self):
        self.submit_should_return_400({
            'command': ''
        })

    def test_integer_command(self):
        self.submit_should_return_400({
            'command': 1234,
        })

    def test_invalid_option(self):
        self.submit_should_return_400({
            'command': 'ls',
            'options': {
                'invalidOption': 'foo',
            },
        })


class TestLSFSubmitError(BaseAPITest):
    def test_invalid_queue(self):
        callback_server = self.create_callback_server([200])

        submit_data = {
            'command': 'invalidcommandnamethatcannotbefoundanywhere foo',
            'options': {
                'queue': 'thisisareallybogusqueuename',
            },
            'webhooks': {
                'error': callback_server.url,
                'failure': callback_server.url,
                'success': callback_server.url,
            },
        }

        response = self.post(self.jobs_url, submit_data)

        pprint.pprint(response.headers)
        pprint.pprint(response.DATA)
        self.assertEqual(response.status_code, 201)

        webhook_data = callback_server.stop()[0]

        self.assertEqual(webhook_data['statusHistory'][0]['status'], 'NEW')
        self.assertEqual(webhook_data['statusHistory'][1]['status'], 'ERRORED')
