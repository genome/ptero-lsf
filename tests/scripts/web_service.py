from ptero_lsf.api.wsgi import app
import os

port = int(os.environ['PTERO_LSF_PORT'])
host = os.environ['PTERO_LSF_HOST']


app.run(host=host, port=port, debug=False, use_reloader=False)
