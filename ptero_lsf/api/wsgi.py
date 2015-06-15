from . import application
from ptero_common.logging_configuration import configure_web_logging

app = application.create_app()
configure_web_logging("LSF")
