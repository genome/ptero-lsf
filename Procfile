web: gunicorn ptero_lsf.api.wsgi:app --access-logfile - --error-logfile -
poller: celery worker -A ptero_lsf.implementation.celery_app -Q poll --concurrency 1
updater: celery worker -A ptero_lsf.implementation.celery_app -Q update --concurrency 1
worker:  celery worker -A ptero_lsf.implementation.celery_app -Q lsftask --concurrency 1
http_worker: celery worker -A ptero_lsf.implementation.celery_app -Q http --concurrency 1
scheduler: celery beat -A ptero_lsf.implementation.celery_app
