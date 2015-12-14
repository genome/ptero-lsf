import abc
from ptero_lsf.factories.celeryfactorymixin import CeleryFactoryMixin
from ptero_lsf.factories.dbfactorymixin import DBFactoryMixin


class BigFactory(CeleryFactoryMixin, DBFactoryMixin):
    __metaclass__ = abc.ABCMeta

    def __init__(self, database_url, celery_app=None):
        CeleryFactoryMixin.__init__(self, celery_app)
        DBFactoryMixin.__init__(self, database_url)
        self._initialized = False

    @abc.abstractproperty
    def backend(self):
        pass

    @abc.abstractproperty
    def base_dir(self):
        pass

    def create_backend(self):
        self._initialize()
        self.db_revision = self.alembic_db_revision()
        return self.backend(session=self.Session(bind=self.engine),
            celery_app=self.celery_app, db_revision=self.db_revision)

    def _initialize(self):
        # Lazy initialize to be pre-fork friendly.
        if not self._initialized:
            self._initialize_celery()
            self._initialize_database()
            self._initialized = True
