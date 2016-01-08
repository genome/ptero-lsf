from .base import BaseAPITest
import pprint
import os


class TestLSFUpdateError(BaseAPITest):
    def test_invalid_job_id(self):
        running = self.create_callback_server([200])
        errored = self.create_callback_server([200])

        submit_data = {
            'command': 'sleep 240',
            'pollingInterval': 1,
            'webhooks': {
                'running': running.url,
                'errored': errored.url,
            },
        }

        self.update_submit_data(submit_data)
        response = self.post(self.jobs_url, submit_data)
        self.print_response(response)
        self.assertEqual(response.status_code, 201)
        self.print_response(self.get(response.headers['Location']))

        running_webhook_data = running.stop()
        pprint.pprint("Running Webhook:\n\n%s" % running_webhook_data)
        set_lsf_job_id_to_1(running_webhook_data[0]['jobId'])

        errored_webhook_data = errored.stop()
        pprint.pprint("Errored Webhook:\n\n%s" % errored_webhook_data)
        kill_lsf_job(running_webhook_data[0]['lsfJobId'])


def set_lsf_job_id_to_1(job_id):
    update_job_sql = "update job set lsf_job_id=1 where id='%s'" % job_id
    update_job_command = 'psql -h localhost -U postgres -d ptero_lsf ' \
        '-c "%s"' % update_job_sql
    print update_job_command
    os.system(update_job_command)


def kill_lsf_job(lsf_job_id):
    os.system("bkill %s" % lsf_job_id)
