from urllib import request
from collections import namedtuple


Response = namedtuple('Response', [
    'content', 'text', 'headers', 'status'
])


class Fetcher:
    def __init__(self, *args, **kwargs):
        pass

    @property
    def cookiejar(self):
        raise NotImplementedError()

    def create_request(self, url):
        req = request.Request(url)
        self.prepare_request(req)
        return req

    def prepare_request(self, request):
        pass

    def process_response(self, response):
        pass

    def head(self, url):
        req = self.create_request(url)
        resp = self.raw_request(req)
        return resp.info().items()

    def get(self, url):
        req = self.create_request(url)
        return self.raw_request(req)
        return resp.read(), resp.info().items()

    def post(self, url, data):
        raise NotImplementedError()

    def raw_request(self, req):
        resp = request.urlopen(req)
        import ipdb; ipdb.set_trace(); pass
        self.process_response(resp)
        return resp


class RefererMixin:
    pass


class CookieHandlerMixin:
    pass


class ClientHeadersMixin:
    pass


import unittest
import json


class BaseTest(unittest.TestCase):
    BASE = 'http://httpbin.org'

    def test_get(self):
        c = Fetcher()
        resp, headers = c.get(self.BASE + '/get')
        resp = json.loads(resp.decode('utf-8'))
        import ipdb; ipdb.set_trace(); pass

if __name__ == '__main__':
    unittest.main()
