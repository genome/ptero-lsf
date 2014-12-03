from .base import BaseAPITest


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
