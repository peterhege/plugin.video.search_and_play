# coding=utf-8
import importlib
import os
import re
import urllib

import xbmc
import xbmcaddon
import xbmcgui

from resources.lib import settings_repository

addon_info = xbmcaddon.Addon().getAddonInfo
dialog = xbmcgui.Dialog()


def setting(setting_id, value=None):
    if value is not None:
        value = str(value)
        settings_repository.setting(setting_id, value)
    value = xbmcaddon.Addon().getSetting(setting_id)
    if not value:
        return settings_repository.setting(setting_id)
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
    return getattr(module, method)(*args)
