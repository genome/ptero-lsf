from . import backend
import celery

__all__ = ['Factory']


class Factory(object):
    def __init__(self, celery_configuration=None):
        self.celery_configuration = celery_configuration
        self.celery_app = None
        self._initialized = False

    def create_backend(self):
        # Lazy initialize to be pre-fork friendly.
        if not self._initialized:
            self._initialize()
            self._initialzied = True

        return backend.Backend(celery_app=self.celery_app)

    def _initialize(self):
        self.celery_app = celery.Celery('PTero-fork-celery',
                include='ptero_shell_command_fork.implementation.celery_tasks')
        if self.celery_configuration is not None:
            self.celery_app.conf.update(**self.celery_configuration)
