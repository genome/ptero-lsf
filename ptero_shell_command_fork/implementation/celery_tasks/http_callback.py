import celery
import requests
import simplejson

__all__ = ['HTTPCallbackTask']


class HTTPCallbackTask(celery.Task):
    def run(self, url, **kwargs):
        requests.put(url, self.body(kwargs))

    def body(self, kwargs):
        return simplejson.dumps(kwargs)
