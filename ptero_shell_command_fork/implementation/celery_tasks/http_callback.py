import celery
import requests
import simplejson

__all__ = ['HTTPCallbackTask']


class HTTPCallbackTask(celery.Task):
    def run(self, url, **kwargs):
        response = requests.put(url, data=self.body(kwargs),
                headers={'Content-Type': 'application/json'})

    def body(self, kwargs):
        return simplejson.dumps(kwargs)
