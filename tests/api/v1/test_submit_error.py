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
            'webhooks': {
                'errored': callback_server.url,
                'failed': callback_server.url,
                'succeeded': callback_server.url,
            },
        }
        self.update_submit_data(submit_data)
        submit_data.setdefault('options', {})['queue'] =\
                'thisisareallybogusqueuename'

        response = self.post(self.jobs_url, submit_data)

        self.print_response(response)
        self.assertEqual(response.status_code, 201)

        webhook_data = callback_server.stop()
        pprint.pprint(webhook_data)
        self.print_response(self.get(response.headers['Location']))

        data = webhook_data[0]

        self.assertEqual(data['statusHistory'][0]['status'], 'new')
        self.assertEqual(data['statusHistory'][1]['status'], 'errored')
