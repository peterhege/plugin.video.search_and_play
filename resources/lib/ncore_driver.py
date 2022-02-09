# -*- coding: utf-8 -*-
import os
import pickle

import xbmc
import xbmcaddon

from resources.lib.control import setting
import requests

session = None
base_url = 'https://ncore.pro'
endpoint = lambda endpoint: '{base}/{endpoint}.php'.format(base=base_url, endpoint=endpoint)
cookie_file_name = os.path.join(
    xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('profile')).decode('utf-8'),
    'ncore.cookie'
)


def login():
    (user, pwd) = (setting('ncore_user'), setting('ncore_pass'))
    if not user or not pwd:
        return False
    global session
    if session is None:
        user_agent = 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.6 Safari/537.36'
        session = requests.Session()
        session.headers.update({'User-Agent': user_agent})

    if os.path.isfile(cookie_file_name):
        cookie_file = open(cookie_file_name)
        cookies = requests.utils.cookiejar_from_dict(pickle.load(cookie_file))
        session.cookies = cookies

    valid_str = user + ' profilja'

    response = session.get(endpoint('profile'))
    if valid_str not in response.content:
        payload = {'nev': user, 'pass': pwd, 'ne_leptessen_ki': True}
        session.post(endpoint('login'), data=payload)
        response = session.get(endpoint('profile'))
        if valid_str in response.content:
            cookie_file = open(cookie_file_name, 'w')
            pickle.dump(requests.utils.dict_from_cookiejar(session.cookies), cookie_file)
            return True
        return False
    return True


def search_movie(tmdb_data):
    if not login():
        return None
