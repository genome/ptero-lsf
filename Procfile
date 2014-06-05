web: gunicorn ptero_shell_command_fork.api.wsgi:app
worker1: celery worker -n worker1.%h --concurrency 1 -A ptero_shell_command_fork.implementation.celery_app
worker2: celery worker -n worker2.%h --concurrency 1 -A ptero_shell_command_fork.implementation.celery_app
worker3: celery worker -n worker3.%h --concurrency 1 -A ptero_shell_command_fork.implementation.celery_app
worker4: celery worker -n worker4.%h --concurrency 1 -A ptero_shell_command_fork.implementation.celery_app
