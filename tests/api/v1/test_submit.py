from .base import BaseAPITest


class SubmitTest(BaseAPITest):
    def test_submit_small_job(self):
        self.post(self.jobs_url, {'command': 'ls > test-ls-output'})
