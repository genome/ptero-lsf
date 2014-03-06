from .base import DeferredAPITest


class SomeDeferredTest(DeferredAPITest):
    def test_something(self):
        self.client.get('/jobs/7')
