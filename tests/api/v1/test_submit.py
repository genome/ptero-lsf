from .base import BaseAPITest
import os
import time


class SubmitTest(BaseAPITest):
    def test_submit_small_job(self):
        test_data = 'hello small job'
        outfile = self.make_tempfile()
        self.post(self.jobs_url, {
            'command': 'echo "%s"' % test_data,
            'options': {
                'outFile': outfile,
            },
        })

        self.assertTrue(_wait_for_file(outfile))

        data = open(outfile).read()
        self.assertRegexpMatches(data, '%s.*' % test_data)


_MAX_TRIES = 10
_POLLING_INTERVAL = 10
def _wait_for_file(filename):
    for i in xrange(_MAX_TRIES):
        if os.path.isfile(filename):
            return True

        else:
            time.sleep(_POLLING_INTERVAL)

    return False
