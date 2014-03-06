from ...base import BaseAPITest
from ptero_shell_command_fork.api import application


class DeferredAPITest(BaseAPITest):
    def create_wsgi_app(self):
        return application.create_app()
