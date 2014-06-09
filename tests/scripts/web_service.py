from ptero_shell_command_fork.api.wsgi import app
import os

port = int(os.environ.get('PTERO_FORK_PORT', '5200'))
host = os.environ.get('PTERO_FORK_HOST', 'localhost')


app.run(host=host, port=port, debug=False, use_reloader=False)
