from .api import api
import flask


__all__ = ['blueprint']


blueprint = flask.Blueprint('blueprint', 'v1')


api.init_app(blueprint)
