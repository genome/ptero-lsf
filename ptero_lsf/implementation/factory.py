from . import backend
from . import models  # noqa
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic import command
import os
import logging


__all__ = ['Factory']


class Factory(object):
    def __init__(self, database_url, celery_app=None):
        self.celery_app = celery_app
        self.database_url = database_url
        self._initialized = False

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

    def _initialize_celery(self):
        from . import celery_app
        self.celery_app = celery_app.app

    def _initialize_database(self):
        self.engine = create_engine(self.database_url)
        self.alembic_config = alembic_config(self.database_url)
        alembic_upgrade(self.alembic_config, self.engine)
        self.Session = sessionmaker()
        setup_logging()


def alembic_config(db_string):
    alembic_cfg = Config()
    alembic_cfg.set_main_option('version_locations', versions_dir())
    alembic_cfg.set_main_option('script_location', scripts_dir())
    alembic_cfg.set_main_option('url', db_string)
    return alembic_cfg


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


def base_dir():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def versions_dir():
    return os.path.join(base_dir(), 'alembic', 'versions')


def scripts_dir():
    return os.path.join(base_dir(), 'alembic')
