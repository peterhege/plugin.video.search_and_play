# -*- coding: utf-8 -*-
import json
import os

import xbmc
import xbmcaddon
import xbmcgui
import tmdbsimple as tmdb

from resources.lib import qbittorrent_driver, control, library_driver
from resources.lib.control import setting, get_media

DOWNLOAD_PENDING_FILE = os.path.join(
    xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('profile')).decode('utf-8'),
    'download_pending.json'
)

if not os.path.exists(DOWNLOAD_PENDING_FILE):
    with open(DOWNLOAD_PENDING_FILE, 'w') as df:
        json.dump({}, df)


def add_pending(hash, tmdb_id):
    with open(DOWNLOAD_PENDING_FILE, 'r') as df:
        pending = json.load(df)
    with open(DOWNLOAD_PENDING_FILE, 'w') as df:
        pending[hash] = tmdb_id
        json.dump(pending, df)


def watch():
    try:
        tmdb.API_KEY = setting('tmdb_key')
        with open(DOWNLOAD_PENDING_FILE, 'r') as df:
            pending = json.load(df)

        if not pending:
            return

        hashes = [h for h in pending.keys()]
        pending_torrents = qbittorrent_driver.get_by_hash(hashes)
        done = False

        for torrent_info in pending_torrents:
            if float(torrent_info['progress']) < 1:
                continue
            done = True
            tmdb_data = tmdb.Movies(pending[torrent_info['hash']]).info(language=xbmc.getLanguage(xbmc.ISO_639_1))
            control.notification(tmdb_data, 'end')

            del pending[torrent_info['hash']]

        if done:
            library_driver.update_library()

        with open(DOWNLOAD_PENDING_FILE, 'w') as df:
            json.dump(pending, df)
    except Exception as e:
        xbmcgui.Dialog().notification('Search and Play ERROR', 'download_manager.watch: {}'.format(str(e)),
                                      get_media('icon.png'))
        xbmc.log('download_manager.watch Error: {}'.format(str(e)))

    try:
        if qbittorrent_driver.session:
            qbittorrent_driver.session.close()
    except Exception as e:
        xbmcgui.Dialog().notification('Search and Play ERROR', 'download_manager.watch: {}'.format(str(e)),
                                      get_media('icon.png'))
        xbmc.log('download_manager.watch Error: {}'.format(str(e)))
    qbittorrent_driver.session = None
