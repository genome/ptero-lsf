from .base import BaseAPITest
import simplejson


class TestMockWebserver(BaseAPITest):
    def test_mock_webserver_works(self):
        callback_server = self.create_callback_server([302])
        import requests
        request_body = {"bob": "hi im your friend"}
        response = requests.put(callback_server.url,
                simplejson.dumps(request_body))
        self.assertEqual(302, response.status_code)

        datas = callback_server.stop()
        self.assertEqual(request_body, datas[0])
