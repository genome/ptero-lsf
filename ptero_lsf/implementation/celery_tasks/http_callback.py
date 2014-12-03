import celery
import json
import requests

__all__ = ['HTTPCallbackTask']


class HTTPCallbackTask(celery.Task):
    ignore_result = True
    def run(self, url, **kwargs):
        response = requests.put(url, data=self.body(kwargs),
                headers={'Content-Type': 'application/json'})

    def body(self, kwargs):
        return json.dumps(kwargs)
