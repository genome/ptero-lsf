from .base import BaseAPITest
import pprint


class KillTest(BaseAPITest):
    def test_killing_job_after_scheduled(self):
        initial_cb_server = self.create_callback_server([200])
        final_cb_server = self.create_callback_server([200, 200])

        submit_data = {
            'command': 'sleep 8675309',
            'pollingInterval': 3,
            'options': {
                'numProcessors': 1,
            },
            'rLimits': {
                'RSS': 1000000,
            },
            'webhooks': {
                'submitted': initial_cb_server.url,
                'canceled': final_cb_server.url,
                'failed': final_cb_server.url,
            },
        }
        self.update_submit_data(submit_data)

        response = self.post(self.jobs_url, submit_data)
        job_url = response.headers['Location']
        self.print_response(response)

        self.assertIn('jobId', response.DATA)
        self.assertEqual(response.status_code, 201)

        webhook_data = initial_cb_server.stop()
        pprint.pprint(webhook_data)

        self.patch(job_url, {'status': 'canceled'})

        webhook_data = final_cb_server.stop()
        pprint.pprint(webhook_data)
