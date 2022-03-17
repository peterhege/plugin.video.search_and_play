# -*- coding: utf-8 -*-

import json
import os
import threading
import time
import smtplib

import xbmc
import xbmcaddon
import tmdbsimple as tmdb
import xbmcgui

from resources.lib import ncore_driver, qbittorrent_driver, library_driver
from resources.lib.control import setting, get_media
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

AVAILABLE_FILE = os.path.join(xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('profile')).decode('utf-8'),
                              'download.json')
__TMDB_IMAGE_BASE__ = 'https://image.tmdb.org/t/p/original'

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
        lang_found = len(query['languages']) == 0 or lang in query['languages']
        quality_found = len(query['qualities']) == 0 or quality in query['qualities']
        if lang_found and quality_found:
            found.append(torrent_id)

    if not found:
        return

    torrent_id = found[0]

    if query['download']:
        torrent_info = ncore_driver.download(torrent_id, False)
        x = threading.Thread(target=download_watch, args=(torrent_info, tmdb_data))
        x.start()

    del search['movie'][tmdb_id]
    save()

    notification(tmdb_data, 'start' if query['download'] else 'available')


def download_watch(torrent_info, tmdb_data):
    progress = 0

    while progress < 1:
        progress = qbittorrent_driver.get_torrent_progress(torrent_info['hash'])
        time.sleep(10)

    library_driver.update_library()
    notification(tmdb_data, 'end')


def notification(tmdb_data, notification_type):
    s = xbmcaddon.Addon().getSetting
    if notification_type == 'available':
        message = 'A(z) {} film letölthető'
    elif notification_type == 'start':
        message = 'Megkezdtem a(z) {} letöltését'
    else:
        message = 'A(z) {} letöltése befejeződött.'

    message = message.format(tmdb_data['title'].encode('utf-8'))

    xbmcgui.Dialog().notification('Search and Play', message, get_media('icon.png'))

    if not (s('email_host') and s('email_port') and s('email_user') and s('email_pwd')):
        return

    recipients = []
    for i in range(5):
        try:
            if s('email_address_{}'.format(i)):
                recipients.append(s('email_address_{}'.format(i)))
        except Exception as e:
            pass

    if not recipients:
        return
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = '{} - {}'.format(tmdb_data['title'].encode('utf-8'), time.time())
        msg['From'] = 'Search and Play <{}>'.format(s('email_user'))
        msg['To'] = ', '.join(recipients)

        html = """\
        <html>
          <head></head>
          <body style="text-align:center;">
            <h1>{title}</h1>
            <img style="width:400px;border-radius:10px;" src="{img}">
          </body>
        </html>
        """.format(
            title=message,
            img='{}/{}'.format(__TMDB_IMAGE_BASE__, tmdb_data['poster_path'])
        )

        part1 = MIMEText(message, 'plain')
        part2 = MIMEText(html, 'html')

        msg.attach(part1)
        msg.attach(part2)

        mail = smtplib.SMTP(s('email_host'), s('email_port'))

        mail.ehlo()
        mail.starttls()

        mail.login(s('email_user'), s('email_pwd'))
        mail.sendmail(s('email_user'), recipients, msg.as_string())
        mail.quit()
    except Exception as e:
        xbmcgui.Dialog().ok('Hiba', e.message, xbmcgui.NOTIFICATION_ERROR)
