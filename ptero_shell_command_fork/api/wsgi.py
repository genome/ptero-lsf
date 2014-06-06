from ptero_shell_command_fork.api import application
import os

app = application.create_app()


if __name__ == '__main__':
    port = int(os.environ.get('PTERO_FORK_PORT', '5200'))
    host = os.environ.get('PTERO_FORK_HOST', 'localhost')
    app.run(port=port, host=host)
