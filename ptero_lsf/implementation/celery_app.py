from celery.signals import worker_init, setup_logging
from factory import Factory
from ptero_common.logging_configuration import configure_celery_logging
import celery
import os
import sqlalchemy


TASK_PATH = 'ptero_lsf.implementation.celery_tasks'


app = celery.Celery('PTero-LSF-celery', include=TASK_PATH)


_DEFAULT_CELERY_CONFIG = {
    'CELERY_BROKER_URL': 'amqp://localhost',
    'CELERY_RESULT_BACKEND': 'redis://localhost',
    'CELERY_ACCEPT_CONTENT': ['json'],
    'CELERY_ACKS_LATE': True,
    'CELERY_RESULT_SERIALIZER': 'json',
    'CELERY_TASK_SERIALIZER': 'json',
    'CELERY_TRACK_STARTED': True,
    'CELERYD_PREFETCH_MULTIPLIER': 10,
}
for var, default in _DEFAULT_CELERY_CONFIG.iteritems():
    if var in os.environ:
        app.conf[var] = os.environ[var]
    else:
        app.conf[var] = default


app.conf['CELERYBEAT_SCHEDULE'] = {
    'choose-jobs-to-poll': {
        'task': TASK_PATH + '.polling.PollActiveJobs',
        'schedule': 10,
    },
}

@setup_logging.connect
def setup_celery_logging(**kwargs):
    configure_celery_logging('LSF')

@worker_init.connect
def initialize_sqlalchemy_session(signal, sender):
    app.factory = Factory(
        database_url=os.environ.get('PTERO_LSF_DB_STRING',
            'sqlite://'), celery_app=app)
