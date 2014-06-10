from ptero_shell_command_fork.api.wsgi import app
import os

port = int(os.environ['PTERO_FORK_PORT'])
host = os.environ['PTERO_FORK_HOST']


app.run(host=host, port=port, debug=False, use_reloader=False)
