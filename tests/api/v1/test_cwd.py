from .base import BaseAPITest
import pprint


class TestCwd(BaseAPITest):
    def test_successful_cd(self):
        callback_server = self.create_callback_server([200])

        outfile = self.make_tempfile()
        cwd = self.make_tempdir()

        submit_data = {
            'command': 'pwd',
            'pollingInterval': 30,
            'options': {
                'outFile': outfile,
            },
            'webhooks': {
                'error': callback_server.url,
                'failure': callback_server.url,
                'success': callback_server.url,
            },
            'cwd': cwd,
        }
        self.set_queue(submit_data)

        response = self.post(self.jobs_url, submit_data)
        self.print_response(response)

        webhook_data = callback_server.stop()
        pprint.pprint(webhook_data)

        status_response = self.get(response.headers['Location'])
        self.assertEqual(status_response.status_code, 200)
        self.print_response(status_response)

        data = open(outfile).read()

        self.assertRegexpMatches(data, '%s.*' % cwd)
