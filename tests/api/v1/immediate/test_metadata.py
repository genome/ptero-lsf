from .base import ImmediateAPITest


class TestMetadata(ImmediateAPITest):
    def test_successful_job_should_have_succeeded_status(self):
        post_response = self.post('/v1/jobs',
                {'command_line': ['/usr/bin/true']})
        get_response = self.get(post_response.headers['Location'])
        self.assertEqual('succeeded', get_response.DATA['status'])
