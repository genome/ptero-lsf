from .base import BaseAPITest
import simplejson


class TestMockWebserver(BaseAPITest):
    def test_mock_webserver_works(self):
        self.start_webserver([302])
        import requests
        request_body = {"bob": "hi im your friend"}
        response = requests.put(self.webhook_url,
                simplejson.dumps(request_body))
        self.assertEqual(302, response.status_code)

        datas = self.stop_webserver()
        self.assertEqual(request_body, datas[0])
