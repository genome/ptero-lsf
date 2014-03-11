from .base import ImmediateAPITest
import os
import signal
import simplejson
import subprocess
import time


_TERMINATE_WAIT_TIME = 0.1


class WebhookTestBase(ImmediateAPITest):
    def setUp(self):
        super(ImmediateAPITest, self).setUp()
        self._webserver = None

    def tearDown(self):
        super(ImmediateAPITest, self).tearDown()
        self.stop_webserver()


    def start_webserver(self, response_codes):
        if self._webserver:
            raise RuntimeError('Cannot start multiple webservers in one test')
        command_line = ['python', self._webserver_path]
        command_line.extend(map(str, response_codes))
        self._webserver = subprocess.Popen(command_line,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self._wait_for_webserver()

    def stop_webserver(self):
        if self._webserver is not None:
            self._kill_webserver()
            stdout, stderr = self._webserver.communicate()
            self._webserver = None
            if stdout:
                return map(simplejson.loads, stdout.split('\n')[:-1])
        return []

    @property
    def webhook_url(self):
        return 'http://localhost:%d/' % self._webserver_port


    def _wait_for_webserver(self):
        time.sleep(1)

    def _kill_webserver(self):
        self._webserver.send_signal(signal.SIGINT)

        time.sleep(_TERMINATE_WAIT_TIME)

        try:
            self._webserver.kill()
        except OSError as e:
            if e.errno != 3:  # errno 3: no such pid
                raise

    @property
    def _webserver_path(self):
        return os.path.join(os.path.dirname(__file__), 'logging_webserver.py')

    @property
    def _webserver_port(self):
        return 5112


class TestMockWebserver(WebhookTestBase):
    def test_mock_webserver_works(self):
        self.start_webserver([302])
        import requests
        request_body = {"bob": "hi im your friend"}
        response = requests.put(self.webhook_url,
                simplejson.dumps(request_body))
        self.assertEqual(302, response.status_code)

        datas = self.stop_webserver()
        self.assertEqual(request_body, datas[0])


class TestWebhooks(WebhookTestBase):
    def test_begun_webhook(self):
        self.start_webserver([200])

        post_response = self.post('/v1/jobs', {
            'command_line': ['true'],
            'callbacks': {
                'begun': self.webhook_url,
            },
        })

        webhook_data = self.stop_webserver()
        expected_data = [
            {'status': 'begun'},
        ]
        self.assertEqual(expected_data, webhook_data)
