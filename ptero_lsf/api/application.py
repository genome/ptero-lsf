from . import v1
from ..implementation import Factory
from ptero_common import nicer_logging
import flask
import os


LOG = nicer_logging.getLogger(__name__)


__all__ = ['create_app']


def create_app():
    factory = Factory(database_url=os.environ['PTERO_LSF_DB_STRING'])

    app = _create_app_from_blueprints()
    app.config['RESTFUL_JSON'] = {
            'indent': 4,
            'sort_keys': True,
    }

    _attach_factory_to_app(factory, app)

    return app


def _create_app_from_blueprints():
    app = flask.Flask('PTero LSF Service')
    app.register_blueprint(v1.blueprint, url_prefix='/v1')

    return app


def _attach_factory_to_app(factory, app):
    @app.before_request
    def before_request():
        try:
            flask.g.backend = factory.create_backend()
        except:
            LOG.exception("Exception raised while creating backend")
            raise
        finally:
            if flask.g.backend is None:
                LOG.critical("Failed to create backend. Aborting request.")
                flask.abort(500)

    @app.teardown_request
    def teardown_request(exception):
        flask.g.backend.cleanup()
