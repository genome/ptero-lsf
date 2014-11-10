from .base import BaseAPITest
import simplejson


class TestUmask(BaseAPITest):
    def test_umask_0000_set_for_job(self):
        _test_umask_set_for_job(self, 0000)

    def test_umask_0777_set_for_job(self):
        _test_umask_set_for_job(self, 0777)

def _test_umask_set_for_job(self, umask):
    callback_server = self.create_callback_server([200])

    post_data = {
        'commandLine': ['/usr/bin/umask'],
        'user': self.job_user,
        'workingDirectory': self.job_working_directory,
        'umask': umask,
        'callbacks': {
            'ended': callback_server.url,
        },
    }

    self.post(self.jobs_url, post_data)

    webhook_data = callback_server.stop()
    actual_umask = webhook_data[0]['stdout'].strip('\n')
    self.assertEqual(oct(umask).zfill(4), actual_umask)
