# coding=utf-8
import importlib
import os
import re
import smtplib
import time
import urllib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import xbmc
import xbmcaddon
import xbmcgui

from resources.lib import settings_repository

addon_info = xbmcaddon.Addon().getAddonInfo
dialog = xbmcgui.Dialog()
__TMDB_IMAGE_BASE__ = 'https://image.tmdb.org/t/p/original'


def setting(setting_id, value=None):
    if value is not None:
        value = str(value)
        settings_repository.setting(setting_id, value)
    value = xbmcaddon.Addon().getSetting(setting_id)
    if not value:
        return settings_repository.setting(setting_id)
    if value in ['false', 'true']:
        return value == 'true'
    return value


def media_path():
    try:
        return os.path.join(addon_info('path'), 'resources', 'media')
    except:
        return os.path.join('resources', 'media')


def get_media(name):
    return os.path.join(media_path(), name)


def build_query(parameters):
    encode = lambda parameter: urllib.quote_plus(str(parameter))
    return '&'.join(['{key}={value}'.format(key=key, value=encode(parameters[key])) for key in parameters])


def call_user_func(s):
    (module, method) = s.split('.')
    args = re.search(r'\((.*)\)$', method).groups()[0].split(',')
    method = re.sub(r'\(.*\)$', '', method)
    module = importlib.import_module('resources.lib.{module}'.format(module=module))

    for i in range(len(args)):
        if re.match(r'^0[^.]0*', args[i]):
            continue
        try:
            args[i] = int(args[i])
            continue
        except:
            pass
        try:
            args[i] = float(args[i])
            continue
        except:
            pass

    return getattr(module, method)(*args)


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
