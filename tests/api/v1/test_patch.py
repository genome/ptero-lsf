from .base import BaseAPITest
import pprint


class PatchTest(BaseAPITest):
    def test_patching(self):
        cb_server = self.create_callback_server([200])

        submit_data = {
            'command': 'true',
            'pollingInterval': 3,
            'webhooks': {
                'succeeded': cb_server.url,
            },
        }
        self.update_submit_data(submit_data)

        response = self.post(self.jobs_url, submit_data)
        job_url = response.headers['Location']
        self.print_response(response)

        webhook_data = cb_server.stop()
        pprint.pprint(webhook_data)

        # patch with custom message
        patch_response = self.patch(job_url,
                {'status': ['failed', 'Some custom message']})
        self.assertEqual(patch_response.status_code, 200)

        get_response = self.get(job_url)
        self.assertEqual('Some custom message',
                get_response.DATA['statusHistory'][-1]['message'])

        # patch status without custom message
        patch_response = self.patch(job_url,
                {'status': 'errored'})
        self.assertEqual(patch_response.status_code, 200)

        get_response = self.get(job_url)
        self.assertEqual('Updated via PATCH request',
                get_response.DATA['statusHistory'][-1]['message'])

        # patch unsported field
        patch_response = self.patch(job_url,
                {'foo': 'bar'})
        self.assertEqual(patch_response.status_code, 400)
