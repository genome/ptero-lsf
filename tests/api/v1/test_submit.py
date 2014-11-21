from .base import BaseAPITest


class SubmitTest(BaseAPITest):
    def test_submit_small_job(self):
        outfile = self.make_tempfile()
        self.post(self.jobs_url, {'command': 'ls > %s' % outfile})
