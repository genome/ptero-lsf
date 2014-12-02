import abc
import os
import platform
import pwd
import requests
import simplejson
import subprocess
import tempfile
import time
import unittest

__all__ = ['BaseAPITest']


class CallbackServer:
    def __init__(self, response_codes):
        self._response_codes = response_codes
        self._webserver = None

    def start(self):
        if self._webserver:
            raise RuntimeError('Cannot start multiple webservers in one test')
        command_line = ['python', self._path,
                '--stop-after', str(self._timeout),
                '--response-codes']
        command_line.extend(map(str, self._response_codes))
        self._webserver = subprocess.Popen(command_line,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self._wait()
        self._port = int(self._webserver.stderr.readline().rstrip())

    def stop(self):
        if self._webserver is not None:
            stdout, stderr = self._webserver.communicate()
            self._webserver = None
            if stdout:
                return map(simplejson.loads, stdout.split('\n')[:-1])
        return []

    def _wait(self):
        time.sleep(1)

    @property
    def url(self):
        return 'http://localhost:%d/' % self._port

    @property
    def _path(self):
        return os.path.join(os.path.dirname(__file__), 'logging_webserver.py')

    @property
    def _timeout(self):
        return 10


class BaseAPITest(unittest.TestCase):
    __metaclass__ = abc.ABCMeta

    def setUp(self):
        self.api_host = os.environ['PTERO_LSF_HOST']
        self.api_port = os.environ['PTERO_LSF_PORT']
        self.tempdir = os.environ['PTERO_LSF_TEST_NETWORK_TEMP']

        if platform.system() == 'Darwin':
            self.job_working_directory = tempfile.mkdtemp(dir='/private/tmp')
        else:
            self.job_working_directory = tempfile.mkdtemp()

    def tearDown(self):
        os.rmdir( self.job_working_directory )

    def create_callback_server(self, response_codes):
        server = CallbackServer(response_codes)
        server.start()
        return server

    @property
    def jobs_url(self):
        return 'http://%s:%s/v1/jobs' % (self.api_host, self.api_port)

    def make_tempfile(self):
        file_object = tempfile.NamedTemporaryFile(dir=self.tempdir)
        name = file_object.name
        file_object.close()
        return name

    @property
    def job_user(self):
        return pwd.getpwuid(os.getuid())[0]

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
