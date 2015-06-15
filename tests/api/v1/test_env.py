from .base import BaseAPITest
import os
import pprint


class TestEnvironment(BaseAPITest):
    def setUp(self):
        super(TestEnvironment, self).setUp()

        self.callback_server = self.create_callback_server([200])

        self.old_environment = dict(os.environ)
        self.test_environment = {
            'SALLY': 'FORTH',
        }

        os.environ.clear()
        os.environ.update(self.test_environment)

    def tearDown(self):
        super(TestEnvironment, self).tearDown()
        os.environ.clear()
        os.environ.update(self.old_environment)

    def test_correct_environment(self):
        outfile = self.make_tempfile()

        submit_data = {
            'command': 'env',
            'pollingInterval': 30,
            'options': {
                'outFile': outfile,
            },
            'webhooks': {
                'errored': self.callback_server.url,
                'failed': self.callback_server.url,
                'succeeded': self.callback_server.url,
            },
            'cwd': self.job_working_directory,
            'environment': self.test_environment,
        }
        self.update_submit_data(submit_data)

        response = self.post(self.jobs_url, submit_data)
        self.print_response(response)

        webhook_data = self.callback_server.stop()
        pprint.pprint(webhook_data)

        status_response = self.get(response.headers['Location'])
        self.assertEqual(status_response.status_code, 200)
        self.print_response(status_response)

        data = open(outfile).read()

        self.assertRegexpMatches(data, 'SALLY=FORTH\n')
        self.assertRegexpMatches(data, 'LSF_LIBDIR=')
        self.assertRegexpMatches(data, 'LSF_BINDIR=')
