import celery
import requests
import simplejson

__all__ = ['HTTPCallbackTask']


class HTTPCallbackTask(celery.Task):
    def run(self, url, status):
        requests.put(url, self.body(status))

    def body(self, status):
        return simplejson.dumps({
            'status': status,
        })
