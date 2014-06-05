import abc
import os
import requests
import simplejson
import subprocess
import time
import unittest

__all__ = ['BaseAPITest']


class BaseAPITest(unittest.TestCase):
    __metaclass__ = abc.ABCMeta

    def setUp(self):
        self.api_host = os.environ.setdefault('PTERO_FORK_HOST', 'localhost')
        self.api_port = os.environ.setdefault('PTERO_FORK_PORT', '5200')
        self._webserver = None

    def tearDown(self):
        self.stop_webserver()


    def start_webserver(self, response_codes):
        if self._webserver:
            raise RuntimeError('Cannot start multiple webservers in one test')
        command_line = ['python', self._webserver_path,
                '--port', str(self._webserver_port),
                '--stop-after', str(self._webserver_timeout),
                '--response-codes']
        command_line.extend(map(str, response_codes))
        self._webserver = subprocess.Popen(command_line,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self._wait_for_webserver()

    def stop_webserver(self):
        if self._webserver is not None:
            stdout, stderr = self._webserver.communicate()
            self._webserver = None
            if stdout:
                return map(simplejson.loads, stdout.split('\n')[:-1])
        return []

    def _wait_for_webserver(self):
        time.sleep(1)

    @property
    def webhook_url(self):
        return 'http://localhost:%d/' % self._webserver_port

    @property
    def _webserver_path(self):
        return os.path.join(os.path.dirname(__file__), 'logging_webserver.py')

    @property
    def _webserver_timeout(self):
        return 10

    @property
    def _webserver_port(self):
        return 5112


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
