from . import backend

__all__ = ['Factory']


class Factory(object):
    def __init__(self, celery_configuration=None):
        self.celery_configuration = celery_configuration
        self.celery_app = None
        self._initialized = False

    def create_backend(self):
        self._initialize()
        return backend.Backend(celery_app=self.celery_app)

    def purge(self):
        self._initialize()
        self.celery_app.control.discard_all()

    def _initialize(self):
        # Lazy initialize to be pre-fork friendly.
        if not self._initialized:
            self._initialize_celery()
            self._initialized = True

    def _initialize_celery(self):
        from . import celery_app
        self.celery_app = celery_app.app
        if self.celery_configuration is not None:
            self.celery_app.conf.update(**self.celery_configuration)
