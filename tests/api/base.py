import abc
import simplejson
import os
import unittest

__all__ = ['BaseAPITest']


class BaseAPITest(unittest.TestCase):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def create_wsgi_app(self):
        pass  # pragma: no cover

    def setUp(self):
        self.app = self.create_wsgi_app()
        self.client = self.app.test_client()

    def get(self, url, **kwargs):
        return _deserialize_response(self.client.get(url, query_string=kwargs))

    def patch(self, url, data):
        return _deserialize_response(self.client.patch(url,
            content_type='application/json', data=simplejson.dumps(data)))

    def post(self, url, data):
        return _deserialize_response(self.client.post(url,
            content_type='application/json', data=simplejson.dumps(data)))

    def put(self, url, data):
        return _deserialize_response(self.client.put(url,
            content_type='application/json', data=simplejson.dumps(data)))


def _deserialize_response(response):
    try:
        response.DATA = simplejson.loads(response.data)
    except simplejson.JSONDecodeError:
        pass
    return response
