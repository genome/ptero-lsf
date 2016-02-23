from .base import BaseAPITest
from ptero_common.view_wrapper import NO_SUCH_ENTITY_STATUS_CODE
import uuid


class BadRequestTest(BaseAPITest):
    def _fake_job_url(self):
        fake_job_id = str(uuid.uuid4())
        url = '%s/%s' % (self.jobs_url, fake_job_id)
        return url

    def test_getting_non_existent_job(self):
        response = self.get(self._fake_job_url())
        self.assertEqual(response.status_code, NO_SUCH_ENTITY_STATUS_CODE)

    def test_patching_non_existent_job(self):
        response = self.patch(self._fake_job_url(),
                {'status': 'errored'})
        self.assertEqual(response.status_code, NO_SUCH_ENTITY_STATUS_CODE)
