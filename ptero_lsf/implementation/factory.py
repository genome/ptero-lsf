from . import backend
from . import models  # noqa
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker
from ptero_lsf.alembic.config import alembic_config
from alembic.script import ScriptDirectory
from alembic import command
import abc
import os
import logging


__all__ = ['Factory']


class CeleryFactoryMixin(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, celery_app=None):
        self.celery_app = celery_app

    def _initialize_celery(self):
        if self.celery_app is None:
            from . import celery_app
            self.celery_app = celery_app.app


class DBFactoryMixin(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, database_url):
        self.database_url = database_url

    @abc.abstractproperty
    def base_dir():
        pass

    def _initialize_database(self):
        self.engine = create_engine(self.database_url)
        self.alembic_config = alembic_config(self.base_dir(), self.database_url)
        alembic_upgrade(self.alembic_config, self.engine)
        self.Session = sessionmaker()
        setup_logging()


def alembic_upgrade(alembic_config, engine):
    with engine.begin() as connection:
        alembic_config.attributes['connection'] = connection
        command.upgrade(alembic_config, "head")


def alembic_db_revision(alembic_config):
    return ScriptDirectory.from_config(
            alembic_config).as_revision_number("head")


def setup_logging():
    logging.getLogger('sqlalchemy.engine').setLevel(getattr(logging,
            os.environ.get('PTERO_LSF_ORM_LOG_LEVEL', 'WARN').upper()))


class BigFactory(CeleryFactoryMixin, DBFactoryMixin):
    __metaclass__ = abc.ABCMeta

    def __init__(self, database_url, celery_app=None):
        CeleryFactoryMixin.__init__(self, celery_app)
        DBFactoryMixin.__init__(self, database_url)
        self._initialized = False

    @abc.abstractproperty
    def base_dir(self):
        pass

    def create_backend(self):
        self._initialize()
        self.db_revision = alembic_db_revision(self.alembic_config)
        return backend.Backend(session=self.Session(bind=self.engine),
            celery_app=self.celery_app, db_revision=self.db_revision)

    def _initialize(self):
        # Lazy initialize to be pre-fork friendly.
        if not self._initialized:
            self._initialize_celery()
            self._initialize_database()
            self._initialized = True


class Factory(BigFactory):
    def base_dir(self):
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
