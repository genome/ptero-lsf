web: gunicorn ptero_shell_command_fork.api.wsgi:app
worker: celery worker --concurrency 1 -A ptero_shell_command_fork.implementation.celery_app
