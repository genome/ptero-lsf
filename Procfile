web: gunicorn --bind 0.0.0.0:$PTERO_LSF_PORT ptero_lsf.api.wsgi:app --access-logfile - --error-logfile -
poller: celery worker -n Xworker.%h.$PORT --pool=eventlet --concurrency 1 -A ptero_lsf.implementation.celery_app -Q poll
updater: celery worker -A ptero_lsf.implementation.celery_app -Q update
worker:  celery worker -A ptero_lsf.implementation.celery_app -Q lsftask
http_worker: celery worker -A ptero_lsf.implementation.celery_app -Q http
scheduler: celery beat --schedule var/celerybeat-schedule -A ptero_lsf.implementation.celery_app
