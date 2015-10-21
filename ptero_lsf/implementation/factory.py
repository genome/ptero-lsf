from . import backend
from . import models  # noqa
import sqlalchemy
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic import command
import os
import logging


def base_dir():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


alembic_cfg = Config()
versions_dir = os.path.join(base_dir(), 'alembic', 'versions')
alembic_cfg.set_main_option('version_locations', versions_dir)
scripts_dir = os.path.join(base_dir(), 'alembic')
alembic_cfg.set_main_option('script_location', scripts_dir)
alembic_cfg.set_main_option('url', os.environ['PTERO_LSF_DB_STRING'])


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

        with self._engine.begin() as connection:
            alembic_cfg.attributes['connection'] = connection
            script = ScriptDirectory.from_config(alembic_cfg)
            current_revision = script.as_revision_number("head")

        return current_revision

    def _initialize_sqlalchemy(self):
        logging.getLogger('sqlalchemy.engine').setLevel(getattr(logging,
                os.environ.get('PTERO_WORKFLOW_ORM_LOG_LEVEL', 'WARN').upper()))
        self._engine = sqlalchemy.create_engine(
            self.database_url, max_overflow=100)

        with self._engine.begin() as connection:
            alembic_cfg.attributes['connection'] = connection
            command.upgrade(alembic_cfg, "head")

        self._Session = sqlalchemy.orm.sessionmaker(bind=self._engine)

    def _initialize_celery(self):
        from . import celery_app
        self.celery_app = celery_app.app
