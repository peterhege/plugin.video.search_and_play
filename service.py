# -*- coding: utf-8 -*-
import datetime
import threading
import time

import xbmcgui

from resources.lib import qbittorrent_driver, available_manager, download_manager
from resources.lib.control import get_media

xbmcgui.Dialog().notification('Search and Play', 'Háttérfolymat elindult', get_media('icon.png'))

cron = {}


def start(callback):
    x = threading.Thread(target=callback)
    x.start()


def run(key, period):
    n = datetime.datetime.now()
    if key not in cron:
        cron[key] = n
        return True
    (count, interval) = period.split(' ')
    r = cron[key] + datetime.timedelta(**{interval: float(count)})
    if r > n:
        return False
    cron[key] = n
    return True


while True:
    if run('space_free', '5 minutes'):
        start(qbittorrent_driver.free_up_storage_space)
    if run('download', '1 hours'):
        start(available_manager.research_movies)
    if run('pending', '30 seconds'):
        start(download_manager.watch)
    time.sleep(.5)
