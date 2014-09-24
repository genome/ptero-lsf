from ptero_shell_command.api.wsgi import app
import os

port = int(os.environ['PTERO_SHELL_COMMAND_PORT'])
host = os.environ['PTERO_SHELL_COMMAND_HOST']


app.run(host=host, port=port, debug=False, use_reloader=False)
