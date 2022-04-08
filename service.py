# -*- coding: utf-8 -*-
import datetime
import threading
import time

import xbmc
import xbmcgui

from resources.lib import qbittorrent_driver, available_manager, download_manager, web_interface, ncore_driver
from resources.lib.control import get_media, setting

xbmcgui.Dialog().notification('Search and Play', 'Háttérfolymat elindult', get_media('icon.png'))

cron = {}


def start(callback, key=None):
    x = threading.Thread(target=callback)
    x.start()
    if key is None:
        return
    if key not in cron:
        cron[key] = {'run': datetime.datetime.now(), 'thread': None}
    cron[key]['thread'] = x


def run(key, period):
    n = datetime.datetime.now()
    if key not in cron:
        cron[key] = {'run': n, 'thread': None}
        return True
    (count, interval) = period.split(' ')
    r = cron[key]['run'] + datetime.timedelta(**{interval: float(count)})

    if r > n or (cron[key]['thread'] is not None and cron[key]['thread'].isAlive()):
        return False

    cron[key]['run'] = n
    return True


monitor = xbmc.Monitor()
web_interface_running = False

while not monitor.abortRequested():
    if run('space_free', '5 minutes'):
        start(qbittorrent_driver.free_up_storage_space, 'space_free')
    if run('download', '1 hours'):
        start(available_manager.research_movies, 'download')
    if run('pending', '30 seconds'):
        start(download_manager.watch, 'pending')
    if run('news', '1 days'):
        start(ncore_driver.news, 'news')
    if not web_interface_running and setting('web_interface'):
        start(web_interface.start)
        web_interface_running = True
    if web_interface_running and not setting('web_interface'):
        web_interface.stop()
        web_interface_running = False
    time.sleep(.5)

web_interface.stop()
