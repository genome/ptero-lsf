from alembic import command
from alembic.script import ScriptDirectory
from ptero_lsf.alembic.config import alembic_config
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker
import abc
import logging
import os


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

    def alembic_db_revision(self):
        return ScriptDirectory.from_config(
                self.alembic_config).as_revision_number("head")


def alembic_upgrade(alembic_config, engine):
    with engine.begin() as connection:
        alembic_config.attributes['connection'] = connection
        command.upgrade(alembic_config, "head")


def setup_logging():
    logging.getLogger('sqlalchemy.engine').setLevel(getattr(logging,
            os.environ.get('PTERO_LSF_ORM_LOG_LEVEL', 'WARN').upper()))
