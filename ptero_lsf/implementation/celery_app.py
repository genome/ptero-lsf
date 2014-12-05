from celery.signals import worker_init
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


app.Session = sqlalchemy.orm.sessionmaker()


@worker_init.connect
def initialize_sqlalchemy_session(signal, sender):
    from . import models

    engine = sqlalchemy.create_engine(os.environ['PTERO_LSF_DB_STRING'])
    models.Base.metadata.create_all(engine)
    app.Session.configure(bind=engine)
