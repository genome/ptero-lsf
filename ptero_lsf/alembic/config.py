from alembic.config import Config
import os


def alembic_config(base_dir, db_string):
    config = Config()
    config.set_main_option('version_locations', versions_dir(base_dir))
    config.set_main_option('script_location', scripts_dir(base_dir))
    config.set_main_option('url', db_string)
    return config


def scripts_dir(base_dir):
    return os.path.join(base_dir, 'alembic')


def versions_dir(base_dir):
    return os.path.join(base_dir, 'alembic', 'versions')
