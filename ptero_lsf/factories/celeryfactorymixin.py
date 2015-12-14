import abc


class CeleryFactoryMixin(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, celery_app=None):
        self.celery_app = celery_app

    def _initialize_celery(self):
        if self.celery_app is None:
            from ptero_lsf.implementation.celery_app import app
            self.celery_app = app
