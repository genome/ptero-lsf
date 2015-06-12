from . import backend
from . import models
import sqlalchemy

__all__ = ['Factory']


class Factory(object):
    def __init__(self, database_url, celery_app=None):
        self.celery_app = celery_app
        self.database_url = database_url
        self._initialized = False

    def create_backend(self):
        self._initialize()
        return backend.Backend(session=self._Session(),
                celery_app=self.celery_app)

    def _initialize(self):
        # Lazy initialize to be pre-fork friendly.
        if not self._initialized:
            self._initialize_sqlalchemy()
            self._initialize_celery()
            self._initialized = True

    def _initialize_sqlalchemy(self):
        self._engine = sqlalchemy.create_engine(self.database_url)
        models.Base.metadata.create_all(self._engine)
        self._Session = sqlalchemy.orm.sessionmaker(bind=self._engine)

    def _initialize_celery(self):
        from . import celery_app
        self.celery_app = celery_app.app
