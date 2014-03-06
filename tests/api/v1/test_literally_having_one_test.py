from ..base import APITest
from ptero_shell_command_fork.api import application


class OneTest(APITest):
    def create_wsgi_app(self):
        return application.create_app({'CELERY_ALWAYS_EAGER': True})

    def test_literally_one_thing(self):
        self.client.get('/jobs/7')
