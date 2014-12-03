from ptero_lsf.api.wsgi import app
import os
import logging


logging.basicConfig(level=logging.DEBUG)


port = int(os.environ['PTERO_LSF_PORT'])
host = os.environ['PTERO_LSF_HOST']


app.run(host=host, port=port, debug=False, use_reloader=False)
