from flask.ext.restful import Api
from . import views

__all__ = ['api']


api = Api(default_mediatype='application/json')
api.add_resource(views.JobListView, '/jobs', endpoint='job-list')
api.add_resource(views.JobView, '/jobs/<string:pk>', endpoint='job')

api.add_resource(views.ServerInfo, '/server-info', endpoint='server-info')
