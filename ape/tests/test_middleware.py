import unittest

import mock
from swift.common.swob import Request

from ape.middleware import ApeMiddleware


class FakeApp(object):
    def __call__(self, env, start_response):
        start_response('200 OK', [])
        return ""


class TestApeMiddleware(unittest.TestCase):
    env = { 'REQUEST_METHOD': 'PUT' }
    def test_valid(self):
        req = Request.blank('/v1/a/c/o?temp_url_sig=69c8a34a67f6c4be3dfcae899b9a184b9df958c6&temp_url_expires=1484539024&max_file_size=1073741824&max_file_size_sig=1fbd08db37f4470a6911ddb2302e2dd5656c4104', self.env, None, 'content')
        mw = ApeMiddleware(FakeApp(), None)
        res = req.get_response(mw)
        self.assertEqual(res.status_int, 200)

    def test_invalid(self):
        req = Request.blank('/v1/a/c/o?temp_url_sig=69c8a34a67f6c4be3dfcae899b9a184b9df958c6&temp_url_expires=1484539024&max_file_size=1234567890&max_file_size_sig=1fbd08db37f4470a6911ddb2302e2dd5656c4104', self.env)
        mw = ApeMiddleware(FakeApp(), None)
        res = req.get_response(mw)
        self.assertEqual(res.status_int, 401)

    def test_not_temp_url(self):
        req = Request.blank('/v1/a/c/o', self.env)
        mw = ApeMiddleware(FakeApp(), None)
        res = req.get_response(mw)
        self.assertEqual(res.status_int, 200)

    def test_missing_file_size(self):
        req = Request.blank('/v1/a/c/o?temp_url_sig=c0fbcbd83eff83fafb32d79f3710ef73f26815f0&temp_url_expires=1474532133', self.env)
        mw = ApeMiddleware(FakeApp(), None)
        res = req.get_response(mw)
        self.assertEqual(res.status_int, 401)

    def test_too_long(self):
        req = Request.blank('/v1/a/c/o?temp_url_sig=c0fbcbd83eff83fafb32d79f3710ef73f26815f0&temp_url_expires=1474532133&max_file_size=10&max_file_size_sig=931bc6828b997184885c5848e1d8c6d59da8a25d', self.env, None, 'this input is too long')
        mw = ApeMiddleware(FakeApp(), None)
        res = req.get_response(mw)
        self.assertEqual(res.status_int, 401)

if __name__ == '__main__':
    unittest.main()
