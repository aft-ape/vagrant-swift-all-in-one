import hmac
from hashlib import sha1
from six.moves.urllib.parse import parse_qs

from swift.common.swob import HTTPUnauthorized
from swift.common.utils import register_swift_info, streq_const_time
from swift.common.middleware.tempurl import get_tempurl_keys_from_metadata
from swift.proxy.controllers.base import get_account_info, get_container_info


class ApeMiddleware(object):
    def __init__(self, app, conf):
        self.app = app
        self.conf = conf

    def __call__(self, env, start_response):
        if env['REQUEST_METHOD'] != 'PUT':
            return self.app(env, start_response)
        max_file_size_sig, max_file_size, is_temp_url = self._parse_query(env)
        if not is_temp_url:
            return self.app(env, start_response)
        if not max_file_size_sig or not max_file_size:
            return self._invalid(env, start_response)
        keys = self._get_keys(env)
        has_valid_key = False
        for key in keys:
            sig = hmac.new(key, '%s' % max_file_size, sha1).hexdigest()
            if streq_const_time(max_file_size_sig, sig):
                has_valid_key = True
                break
        if not has_valid_key:
            return self._invalid(env, start_response)
        length = 0
        try:
            length = int(env['CONTENT_LENGTH'])
        except:
            return self._invalid(env, start_response)
        if length > max_file_size:
            return self._invalid(env, start_response)
        return self.app(env, start_response)

    def _parse_query(self, env):
        max_file_size_sig = max_file_size = is_temp_url = None
        qs = parse_qs(env.get('QUERY_STRING', ''), keep_blank_values=True)
        if 'max_file_size_sig' in qs:
            max_file_size_sig = qs['max_file_size_sig'][0]
        if 'max_file_size' in qs:
            try:
                max_file_size = int(qs['max_file_size'][0])
            except ValueError:
                max_file_size = 0
        if 'temp_url_sig' in qs:
            is_temp_url = True
        return max_file_size_sig, max_file_size, is_temp_url

    def _invalid(self, env, start_response):
        if env['REQUEST_METHOD'] == 'HEAD':
            body = None
        else:
            body = '401 Unauthorized: max file size\n'
        return HTTPUnauthorized(body=body)(env, start_response)

    def _get_keys(self, env):
        parts = env['PATH_INFO'].split('/', 4)
        if len(parts) < 4 or parts[0] or parts[1] != 'v1' or not parts[2] or \
                not parts[3]:
            return []

        account_info = get_account_info(env, self.app, swift_source='FP')
        account_keys = get_tempurl_keys_from_metadata(account_info['meta'])

        container_info = get_container_info(env, self.app, swift_source='FP')
        container_keys = get_tempurl_keys_from_metadata(
            container_info.get('meta', []))

        return account_keys + container_keys


def filter_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)
    register_swift_info('ape')
    return lambda app: ApeMiddleware(app, conf)
