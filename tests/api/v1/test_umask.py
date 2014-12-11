from .base import BaseAPITest
import os
import pprint
import stat
import subprocess


class TestUmask(BaseAPITest):
    def test_correct_environment(self):
        callback_server = self.create_callback_server([200])

        outfile = self.make_tempfile()

        submit_data = {
            'command': 'id',
            'pollingInterval': 30,
            'options': {
                'outFile': outfile,
            },
            'webhooks': {
                'error': callback_server.url,
                'failure': callback_server.url,
                'success': callback_server.url,
            },
            'cwd': self.job_working_directory,
            'umask': 0377,
        }
        self.set_queue(submit_data)

        response = self.post(self.jobs_url, submit_data)
        self.print_response(response)

        webhook_data = callback_server.stop()
        pprint.pprint(webhook_data)

        status_response = self.get(response.headers['Location'])
        self.assertEqual(status_response.status_code, 200)
        self.print_response(status_response)

        print subprocess.check_output(['ls', '-lh', outfile])
        self.assertEqual(_get_permission(outfile), 0400)


def _get_permission(filename):
    s = os.stat(filename)
    return s.st_mode & (stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
