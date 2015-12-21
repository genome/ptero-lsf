from ptero_common.factories.bigfactory import BigFactory
from ptero_lsf.implementation import backend
import os


__all__ = ['Factory']


class Factory(BigFactory):

    @property
    def backend_class(self):
        return backend.Backend

    def base_dir(self):
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def _initialize_celery(self):
        if self.celery_app is None:
            from ptero_lsf.implementation.celery_app import app
            self.celery_app = app
