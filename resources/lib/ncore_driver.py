# -*- coding: utf-8 -*-
import base64
import json
import math
import os
import pickle
import re
import time

import xbmc
import xbmcaddon
import xbmcgui

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


def search_movie(tmdb_data, pages=None, found=None, second=None):
    if not login():
        return None
    page = 1 if pages is None else pages.pop(0)
    title = second if second else tmdb_data['title']
    title = title.lower().replace(' ', '.').encode('utf-8')
    url = '{endpoint}?miszerint=seeders&hogyan=DESC&tipus=kivalasztottak_kozott&kivalasztott_tipus=xvid,hd,xvid_hun,hd_hun&mire={query}&oldal={page}' \
        .format(endpoint=endpoint('torrents'), query=title, page=page)
    try:
        url_content = session.get(url).text
    except AttributeError:
        url_content = session.get(url, verify=False).text

    url_content = url_content.encode('utf-8')

    if pages is None:
        pages = re.findall(r'torrents\.php\?oldal=([0-9]+)', url_content, re.MULTILINE)
        pages = sorted([int(page) for page in list(set(pages))])

    torrent_url = re.compile('<div class="box_alap_img">(.*?)<div style="clear:both;">', re.MULTILINE | re.DOTALL) \
        .findall(url_content)
    if not len(torrent_url):
        return found if second else search_movie(tmdb_data, None, found, tmdb_data['original_title'])

    found = found if found else {}
    for row in torrent_url:
        match_id = re.search(r'torrents\.php\?action=details&id=([0-9]+)', row, re.MULTILINE | re.DOTALL)
        match_language = re.search(r'([hH][uU][nN])', row, re.MULTILINE | re.DOTALL)
        match_quality = re.search(r'\.([0-9]+p)?\.', row, re.MULTILINE | re.DOTALL)
        if not match_id or not match_id.groups():
            continue
        match_id = match_id.groups()[0]
        match_language = match_language.groups()[0] if match_language and match_language.groups() and \
                                                       match_language.groups()[0] else 'eng'
        match_quality = match_quality.groups()[0] if match_quality and match_quality.groups() and \
                                                     match_quality.groups()[0] else 'SD'
        key = '{}:{}'.format(match_language, match_quality)
        if key not in found:
            found[key] = match_id

    if len(pages) > 0:
        return search_movie(tmdb_data, pages, found, second)
    if not second:
        return search_movie(tmdb_data, None, found, tmdb_data['original_title'])
    return found


def context(torrents):
    string = json.dumps(torrents)
    b64 = base64.b64encode(string)
    context_key = 'ncore_driver.context_menu({})'.format(b64)
    return {context_key: 'Letöltés'}


def context_menu(torrents):
    torrents = json.loads(base64.b64decode(torrents))
    menu = {}
    for key in sorted(torrents.keys()):
        (language, quality) = key.split(':')
        language = {
            'hun': 'Magyar',
            'eng': 'Angol'
        }[language.lower()]
        quality = quality if quality == 'SD' else 'HD {}'.format(quality)
        menu[torrents[key]] = '[B]{lang}[/B]{tab}{quality}'.format(
            lang=language,
            quality=quality,
            tab=' ' * (int(math.floor((15 - len(language) - len(quality)) * 2.4)) + 5)
        )
    selected_menu = xbmcgui.Dialog().contextmenu(menu.values())
    if selected_menu == -1:
        return
    download(menu.keys()[selected_menu])


def download(torrent_id):
    url = '{endpoint}?action=details&id={torrent_id}'.format(endpoint=endpoint('torrents'), torrent_id=torrent_id)
    xbmcgui.Dialog().ok('url', url)
