from .base import BaseAPITest
import pprint


class SetStdioTest(BaseAPITest):
    def test_patching_stdio(self):
        cb_server = self.create_callback_server([200])

        submit_data = {
            'command': 'true',
            'pollingInterval': 1,
            'options': {
                'numProcessors': 1,
            },
            'webhooks': {
                'succeeded': cb_server.url,
            },
        }
        self.update_submit_data(submit_data)

        response = self.post(self.jobs_url, submit_data)
        job_url = response.headers['Location']
        self.print_response(response)

        self.assertIn('jobId', response.DATA)
        self.assertEqual(response.status_code, 201)

        webhook_data = cb_server.stop()
        pprint.pprint(webhook_data)

        test_stdout = 'Test output message here.'
        test_stderr = 'Test error message here.'

        response = self.patch(job_url, {
            'stdout': test_stdout,
            'stderr': test_stderr})
        self.assertEqual(response.status_code, 200)

        response = self.get(job_url)
        self.assertEqual(response.status_code, 200)

        self.assertIn('stdout', response.DATA)
        self.assertEqual(test_stdout, response.DATA['stdout'])

        self.assertIn('stderr', response.DATA)
        self.assertEqual(test_stderr, response.DATA['stderr'])

        response = self.patch(job_url, {
            'stdout': test_stdout,
            'stderr': test_stderr})
        self.assertEqual(response.status_code, 200)

        response = self.patch(job_url, {
            'stdout': 'A different message'})
        self.assertEqual(response.status_code, 400)
