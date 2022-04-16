# -*- coding: utf-8 -*-

import json
import os

import xbmc
import xbmcaddon
import tmdbsimple as tmdb

from resources.lib import ncore_driver, control
from resources.lib.control import setting

AVAILABLE_FILE = os.path.join(
    xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('profile')).decode('utf-8'),
    'download.json'
)

if not os.path.exists(AVAILABLE_FILE):
    with open(AVAILABLE_FILE, 'w') as df:
        json.dump({}, df)

with open(AVAILABLE_FILE, 'r') as df:
    search = json.load(df)


def search_job(tmdb_id, languages, download, video_type, qualities=None):
    if video_type not in search:
        search[video_type] = {}
    data = search[video_type]

    if not languages or type(languages) != list:
        languages = []
    if not qualities or type(qualities) != list:
        qualities = []
    if tmdb_id not in data:
        data[tmdb_id] = {"qualities": [], "languages": []}

    data[tmdb_id] = {
        "qualities": list(set(data[tmdb_id]['qualities'] + qualities)),
        "languages": list(set(data[tmdb_id]['languages'] + languages)),
        "download": bool(download)
    }

    save()


def save():
    with open(AVAILABLE_FILE, 'w') as df:
        json.dump(search, df)


def research_movies():
    if 'movie' not in search:
        return
    movies = search['movie']

    try:
        tmdb.API_KEY = setting('tmdb_key')
        ncore_driver.login(setting('ncore_user'), setting('ncore_pass'))
    except Exception as e:
        return

    for tmdb_id, query in movies.items():
        try:
            research_movie(tmdb_id, query)
        except Exception as e:
            return


def research_movie(tmdb_id, query):
    tmdb_data = tmdb.Movies(tmdb_id).info(language=xbmc.getLanguage(xbmc.ISO_639_1))

    torrents = ncore_driver.search_movie(tmdb_data)

    if not torrents:
        return

    found = []

    for key, torrent_id in torrents.items():
        (lang, quality) = key.split(':')
        if lang in ['all', 'imdb_match']:
            continue
        lang_found = len(query['languages']) == 0 or lang in query['languages']
        quality_found = len(query['qualities']) == 0 or quality in query['qualities']
        if lang_found and quality_found:
            found.append(torrent_id)

    if not found:
        return

    torrent_id = found[0]

    if query['download']:
        ncore_driver.TMDB_DATA = tmdb_data
        ncore_driver.download(torrent_id, False)

    del search['movie'][tmdb_id]
    save()

    control.notification(tmdb_data, 'start' if query['download'] else 'available')
