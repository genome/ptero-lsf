web: gunicorn -b 0.0.0.0:$PORT ptero_shell_command_fork.api.wsgi:app
worker: celery worker -n shell_worker.%h.$PORT -A ptero_shell_command_fork.implementation.celery_app
