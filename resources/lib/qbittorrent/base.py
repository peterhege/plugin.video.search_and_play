# -*- coding: utf-8 -*-
import os
import pickle

import requests

try:
    from typing import Union, Match
except:
    pass

REQUESTS_SESSION = None  # type: Union[None,requests.Session]


class AuthenticationError(Exception):
    pass


class Qbittorrent(object):
    headers = {}
    BASE_PATH = ''
    URLS = {}
    response = None  # type: requests.Response

    def __init__(self):
        from . import WEB_UI_HOST, API_VERSION, REQUESTS_TIMEOUT, USER_PATH
        self.base_uri = WEB_UI_HOST.rstrip('/')
        self.base_uri += '/api/v{version}'.format(version=API_VERSION)
        self.cookie_file = os.path.join(USER_PATH, 'qbittorrent.cookie')
        self.session = self._get_or_create_session()
        self.timeout = REQUESTS_TIMEOUT
        self._login()

    def _get_or_create_session(self):
        global REQUESTS_SESSION

        if REQUESTS_SESSION is not None:
            return REQUESTS_SESSION

        REQUESTS_SESSION = requests.Session()
        REQUESTS_SESSION.headers.update({
            'User-Agent': 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.6 Safari/537.36'
        })

        cookies = self._load_cookies()
        if cookies:
            REQUESTS_SESSION.cookies = cookies

        return REQUESTS_SESSION

    def _load_cookies(self):
        if not os.path.exists(self.cookie_file):
            return None
        try:
            return requests.utils.cookiejar_from_dict(pickle.load(open(self.cookie_file)))
        except Exception as e:
            return None

    def _login(self):
        from . import WEB_UI_USER, WEB_UI_PASS
        endpoint = '{base}/auth/login'.format(base=self.base_uri)
        response = self.session.get(endpoint)

        if response.content == 'Ok.':
            return

        payload = {'username': WEB_UI_USER, 'password': WEB_UI_PASS}
        response = self.session.post(endpoint, data=payload)

        if response.content != 'Ok.':
            raise AuthenticationError(response.content)

        cookie_file = open(self.cookie_file, 'w')
        pickle.dump(requests.utils.dict_from_cookiejar(self.session.cookies), cookie_file)

    def _get_path(self, key):
        return self.BASE_PATH + self.URLS[key]

    def _get_complete_url(self, path):
        return '{base_uri}/{path}'.format(base_uri=self.base_uri, path=path)

    def _request(self, method, path, params=None, payload=None, headers=None, files=None):
        kwargs = {'headers': self.headers if headers is None else headers, 'timeout': self.timeout}
        if params is not None:
            kwargs['params'] = params
        if payload is not None:
            kwargs['data'] = payload
        if files is not None:
            kwargs['files'] = files

        url = self._get_complete_url(path)
        base = requests if self.session is None else self.session
        response = base.request(method, url, **kwargs)
        response.raise_for_status()
        response.encoding = 'utf-8'
        self.response = response

        try:
            return response.json()
        except ValueError:
            return response.content

    def _GET(self, path, params=None, headers=None):
        return self._request('GET', path, params=params, headers=headers)

    def _POST(self, path, params=None, payload=None, headers=None, files=None):
        return self._request('POST', path, params=params, payload=payload, headers=headers, files=files)

    def _DELETE(self, path, params=None, payload=None, headers=None):
        return self._request('DELETE', path, params=params, payload=payload, headers=headers)
