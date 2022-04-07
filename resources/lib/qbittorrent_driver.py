# -*- coding: utf-8 -*-
import json
import math
import os
import pickle
import re
import time

import requests
import xbmc
import xbmcaddon
import xbmcgui

from resources.lib import settings_repository, library_driver, context_factory
from resources.lib.control import setting, dialog, get_media

try:
    from typing import Union
except:
    pass

try:
    sys
except:
    import sys

REPLACE_FILE_NAME = None
TMDB_DATA = {}

base_url = setting('qbittorrent_host')
if not base_url:
    base_url = dialog.input('qBittorrent host')
    setting('qbittorrent_host', base_url)
    if not base_url:
        sys.exit()
base_url = base_url.rstrip('/')

session = None  # type: Union[requests.Session,None]

endpoint = lambda endpoint: '{base}/api/v2/{endpoint}'.format(base=base_url, endpoint=endpoint)
cookie_file_name = os.path.join(
    xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('profile')).decode('utf-8'),
    'qbittorrent.cookie'
)

INITED = False


def init():
    global INITED
    if INITED:
        return
    (user, pwd) = (setting('qbittorrent_user'), setting('qbittorrent_pass'))
    if not login(user, pwd):
        (user, pwd) = (settings_repository.setting('qbittorrent_user'), settings_repository.setting('qbittorrent_pass'))
        i = 0
        while not login(user, pwd):
            if i == 5:
                xbmcgui.Dialog().ok('Bejelentkezési hiba', '{} sikertelen próbálkozás. Próbáld meg később.'.format(i))
                return
            xbmcgui.Dialog().notification(
                'Bejelentkezési hiba',
                'Hibás felhasználónév vagy jelszó!',
                xbmcgui.NOTIFICATION_ERROR
            )
            (user, pwd) = get_auth()
            if not user or not pwd:
                return
            i += 1
    INITED = True


def download(torrent_file, save_path, category, show_dialog=True):
    init()
    data = {'savepath': save_path, 'category': 'search_and_play', 'tags': category}
    buffer = open(torrent_file, 'rb')
    files = {'torrents': buffer}
    response = session.post(endpoint('torrents/add'), data=data, files=files)
    buffer.close()
    try:
        os.remove(torrent_file)
    except:
        pass
    if response.status_code != 200:
        xbmcgui.Dialog().ok('qBittorrent hiba', str(response.content))
        return None

    time.sleep(1)
    torrent_info = get_last_torrent()
    torrent_info['files'] = get_torrent_files(torrent_info['hash'])
    global REPLACE_FILE_NAME
    if REPLACE_FILE_NAME:
        for f in torrent_info['files']:
            if not re.search(r'\.(webm|mkv|flv|vob|ogv|ogg|drc|mng|avi|mov|wmv|mp4)$', f['name'].lower()) \
                    or re.search(r'sample', f['name'].lower()):
                continue
            old_path = f['name']
            separator = '/' if '/' in old_path else '\\'
            old_file = os.path.basename(old_path)
            old_file = '.'.join(old_file.split('.')[:-1])
            new_path = old_path.split(separator)
            new_path[-1] = new_path[-1].replace(old_file, REPLACE_FILE_NAME.replace(':', '').decode('utf-8'))
            new_path = separator.join(new_path)
            rename_torrent_file(torrent_info['hash'], old_path.encode('utf-8'), new_path.encode('utf-8'))
            break
        REPLACE_FILE_NAME = None

    if not show_dialog:
        return torrent_info

    play_from = float(setting('play_from'))

    play = xbmcgui.Dialog().yesno(
        'Mit tegyünk?',
        'Lehetőség van lejátszani a videót, amíg tart a letöltés. A lejátszás {play_from}%-nál indul.'.format(
            play_from=play_from),
        nolabel='Csak letöltés', yeslabel='Lejátszás'
    )

    if not play:
        return torrent_info

    set_torrent_first(torrent_info['hash'])
    toggle_sequential_download(torrent_info['hash'])

    progress_dialog = xbmcgui.DialogProgress()
    progress_dialog.create('Letöltés', '{} letöltése...'.format(TMDB_DATA['title'].encode('utf-8')))
    progress = 0
    i = 0
    updated = False
    play_from /= 100
    while progress < play_from:
        time.sleep(.5)
        progress = get_torrent_progress(torrent_info['hash'])
        progress_dialog.update(int((progress * 100) / play_from), '[{}%] {} letöltése{}'.format(
            math.floor(progress * 10000) / 100,
            TMDB_DATA['title'].encode('utf-8'),
            ('.' * i)
        ))

        if progress >= min(0.05, play_from) and not updated:
            library_driver.update_library()
            updated = True

        if progress_dialog.iscanceled():
            remove_torrents([torrent_info['hash']])
            path = os.path.join(torrent_info['save_path'], torrent_info['name']).encode('utf-8')
            try:
                library_data = library_driver.find_movie_by_path(path)['result']['movies'][0]
                library_driver.remove_movie(library_data['movieid'])
            except Exception as e:
                pass
            progress_dialog.close()
            return None

        i = (i + 1) % 4

    progress_dialog.close()

    movie = library_driver.for_movie(TMDB_DATA)
    library_driver.play(movie['movieid'])


def get_torrent_progress(hash):
    init()
    torrent_info = get_torrent_info(hash)
    return float(torrent_info['progress'])


def get_torrent_info(hash):
    init()
    url = '{endpoint}?hashes={hash}'.format(endpoint=endpoint('torrents/info'), hash=hash)
    response = session.get(url)
    return json.loads(response.content)[0]


def set_torrent_first(hash):
    init()
    url = '{endpoint}'.format(endpoint=endpoint('torrents/topPrio'))
    response = session.post(url, {'hashes': hash})
    return response.content


def get_oldest_torrent():
    init()
    url = '{endpoint}?sort=added_on&limit=1&category=search_and_play'
    try:
        response = session.get(url.format(endpoint=endpoint('torrents/info')))
        return json.loads(response.content)[0]
    except Exception as e:
        return None


def rename_torrent_file(hash, old_path, new_path):
    init()
    url = '{endpoint}?hash={hash}&oldPath={old_path}&newPath={new_path}'
    url = url.format(endpoint=endpoint('torrents/renameFile'), hash=hash, old_path=old_path, new_path=new_path)
    response = session.get(url)
    if response.status_code != 200:
        xbmcgui.Dialog().notification('Hiba', response.content, xbmcgui.NOTIFICATION_WARNING)


def get_last_torrent():
    init()
    url = '{endpoint}?sort=added_on&reverse=true&limit=1'
    response = session.get(url.format(endpoint=endpoint('torrents/info')))
    return json.loads(response.content)[0]


def get_torrent_files(hash):
    init()
    url = '{endpoint}?hash={hash}'.format(endpoint=endpoint('torrents/files'), hash=hash)
    response = session.get(url)
    return json.loads(response.content)


def free_up_storage_space():
    if not setting('space_free'):
        return

    min_space = float(setting('space_free_min_space'))
    free_space = get_free_space() / (1024 ** 3)
    if free_space is False or free_space > min_space:
        return

    oldest = get_oldest_torrent()
    if not oldest:
        return

    try:
        path = os.path.join(oldest['save_path'], oldest['name']).encode('utf-8')
        library_data = library_driver.find_movie_by_path(path)['result']['movies'][0]
        library_driver.remove_movie(library_data['movieid'])
    except Exception as e:
        library_data = {'title': oldest['name']}

    remove_torrents([oldest['hash']])

    xbmcgui.Dialog().notification('Search and Play', '{} törölve'.format(library_data['title'].encode('utf-8')),
                                  get_media('icon.png'))

    global session
    try:
        if session:
            session.close()
    except:
        pass
    session = None


def remove_torrents(hashes):
    init()
    hashes = '|'.join(hashes)
    data = {'hashes': hashes, 'deleteFiles': True}
    try:
        return session.post(endpoint('torrents/delete'), data=data)
    except Exception as e:
        return False


def get_free_space():
    init()
    url = '{endpoint}'.format(endpoint=endpoint('sync/maindata'))
    try:
        response = session.get(url)
        return float(json.loads(response.content)['server_state']['free_space_on_disk'])
    except Exception as e:
        return False


def login(user, pwd):
    global session
    if session is None:
        user_agent = 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.6 Safari/537.36'
        session = requests.Session()
        session.headers.update({'User-Agent': user_agent})

    if os.path.isfile(cookie_file_name):
        cookie_file = open(cookie_file_name)
        cookies = requests.utils.cookiejar_from_dict(pickle.load(cookie_file))
        session.cookies = cookies

    response = session.get(endpoint('auth/login'))

    if response.content == 'Fails.':
        payload = {'username': user, 'password': pwd}
        response = session.post(endpoint('auth/login'), data=payload)
        if response.content == 'Ok.':
            cookie_file = open(cookie_file_name, 'w')
            pickle.dump(requests.utils.dict_from_cookiejar(session.cookies), cookie_file)
            return True
    if response.content not in ['Ok.', 'Fails.']:
        xbmcgui.Dialog().ok('Bejelentkezési hiba', response.content)
    return response.content == 'Ok.'


def get_auth():
    user = xbmcgui.Dialog().input('qBittorrent Felhasználónév')
    setting('qbittorrent_user', user)
    if not user:
        return user, None
    pwd = xbmcgui.Dialog().input('qBittorrent Jelszó')
    setting('qbittorrent_pass', pwd)
    return user, pwd


def toggle_sequential_download(hash):
    init()
    url = '{endpoint}?hashes={hash}'.format(endpoint=endpoint('torrents/toggleSequentialDownload'), hash=hash)
    response = session.get(url)


def get_pending():
    init()
    url = '{endpoint}?filter=downloading'.format(endpoint=endpoint('torrents/info'))
    response = session.get(url)
    return json.loads(response.content)


def get_by_hash(hashes):
    hashes = '|'.join(hashes)
    init()
    url = '{endpoint}?hashes={hashes}'.format(endpoint=endpoint('torrents/info'), hashes=hashes)
    response = session.get(url)
    return json.loads(response.content)
