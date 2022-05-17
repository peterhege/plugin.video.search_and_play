# -*- coding: utf-8 -*-

import os

from .base import AuthenticationError
from .application import Application
from .log import Log
from .model import Torrent, Tracker, TrackerCollection
from .sync import Sync
from .transfer import Transfer
from .torrents import Torrents

try:
    import xbmcaddon
    import xbmc

    USER_PATH = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('profile')).decode('utf-8')
    if not USER_PATH:
        raise Exception
    get_setting = xbmcaddon.Addon().getSetting
except:
    USER_PATH = 'user'


    def get_setting(setting_id):
        return {
            'qbittorrent_host': 'http://localhost:8081',
            'qbittorrent_user': 'admin',
            'qbittorrent_pass': 'adminadmin',
            'qbittorrent_api_version': '2'
        }[setting_id]

__all__ = [
    'AuthenticationError', 'Application', 'Log', 'Sync', 'Transfer', 'Torrents', 'Torrent', 'Tracker',
    'TrackerCollection'
]

if not os.path.exists(USER_PATH):
    os.mkdir(USER_PATH)

WEB_UI_HOST = os.environ.get('QBITTORRENT_WEB_UI_HOST', get_setting('qbittorrent_host'))
WEB_UI_USER = os.environ.get('QBITTORRENT_WEB_UI_USER', get_setting('qbittorrent_user'))
WEB_UI_PASS = os.environ.get('QBITTORRENT_WEB_UI_PASS', get_setting('qbittorrent_pass'))
REQUESTS_TIMEOUT = os.environ.get('QBITTORRENT_REQUESTS_TIMEOUT', None)
API_VERSION = os.environ.get('QBITTORRENT_API_VERSION', get_setting('qbittorrent_api_version'))

Torrent.driver = Torrents
Torrent.sync = Sync
