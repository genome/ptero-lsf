import abc
import os
import requests
import simplejson
import unittest

__all__ = ['BaseAPITest']


class BaseAPITest(unittest.TestCase):
    __metaclass__ = abc.ABCMeta

    def setUp(self):
        self.api_host = os.environ.setdefault('PTERO_FORK_HOST', 'localhost')
        self.api_port = os.environ.setdefault('PTERO_FORK_PORT', '5200')

    @property
    def jobs_url(self):
        return 'http://%s:%s/v1/jobs' % (self.api_host, self.api_port)

    def get(self, url, **kwargs):
        return _deserialize_response(requests.get(url, params=kwargs))

    def patch(self, url, data):
        return _deserialize_response(requests.patch(url,
            headers={'content-type': 'application/json'},
            data=simplejson.dumps(data)))

    def post(self, url, data):
        return _deserialize_response(requests.post(url,
            headers={'content-type': 'application/json'},
            data=simplejson.dumps(data)))

    def put(self, url, data):
        return _deserialize_response(requests.put(url,
            headers={'content-type': 'application/json'},
            data=simplejson.dumps(data)))


def _deserialize_response(response):
    response.DATA = response.json()
    return response
