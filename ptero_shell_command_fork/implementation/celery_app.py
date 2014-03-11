import celery
import os


_CONFIG_TO_UPDATE_FROM_ENVIRONMENT = [
    'CELERY_RESULT_BACKEND',
]

app = celery.Celery('PTero-fork-celery',
        include='ptero_shell_command_fork.implementation.celery_tasks')

conf_dict = {
    'CELERY_ACCEPT_CONTENT': ['json'],
    'CELERY_ACKS_LATE': True,
    'CELERY_RESULT_SERIALIZER': 'json',
    'CELERY_TASK_SERIALIZER': 'json',
    'CELERY_TRACK_STARTED': True,
    'CELERYD_PREFETCH_MULTIPLIER': 1,
}
for var in _CONFIG_TO_UPDATE_FROM_ENVIRONMENT:
    if var in os.environ:
        conf_dict[var] = os.environ[var]
app.conf.update(**conf_dict)
