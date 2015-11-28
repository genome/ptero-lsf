from celery.signals import worker_init, setup_logging
from factory import Factory
from ptero_common.logging_configuration import configure_celery_logging
from ptero_common.celery.utils import get_celery_config
import celery
import os


TASK_PATH = 'ptero_lsf.implementation.celery_tasks'

app = celery.Celery('PTero-LSF-celery', include=TASK_PATH)

app.conf['CELERY_ROUTES'] = (
    {
        'ptero_lsf.implementation.celery_tasks.lsf_task.LSFSubmit':
            {'queue': 'lsftask'},
        'ptero_lsf.implementation.celery_tasks.polling.PollActiveJobs':
            {'queue': 'poll'},
        'ptero_lsf.implementation.celery_tasks.job_status.UpdateJobStatus':
            {'queue': 'update'},
        'ptero_common.celery.http.HTTP': {'queue': 'http'},
        'ptero_common.celery.http.HTTPWithResult': {'queue': 'http'},
    },
)

config = get_celery_config('LSF')
app.conf.update(config)

app.conf['CELERYBEAT_SCHEDULE'] = {
    'choose-jobs-to-poll': {
        'task': TASK_PATH + '.polling.PollActiveJobs',
        'schedule': int(os.environ.get('PTERO_LSF_POLL_INTERVAL', 10)),
    },
}


@setup_logging.connect
def setup_celery_logging(**kwargs):
    configure_celery_logging('LSF')


@worker_init.connect
def initialize_sqlalchemy_session(signal, sender):
    app.factory = Factory(
        database_url=os.environ['PTERO_LSF_DB_STRING'], celery_app=app)
