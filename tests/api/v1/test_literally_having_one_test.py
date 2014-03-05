from ..base import APITest


class OneTest(APITest):
    def test_literally_one_thing(self):
        self.client.get('/jobs/7')
