# -*- coding: utf-8 -*-
import re

import xbmc
import xbmcgui
import xbmcplugin

try:
    sys
except:
    import sys


def for_movie(tmdb_data):
    if re.search('netflix', tmdb_data['homepage']):
        xbmcgui.Dialog().ok('homepage', 'netflix')
        return re.search('[0-9]+$', tmdb_data['homepage']).group()
    return None


def context(id):
    return {'netflix_driver.play({id})'.format(id=id): 'Lejátszás Netflixen'}


def play(id):
    playback_url = 'plugin://plugin.video.netflix/play/movie/{id}'.format(id=id)
    item = xbmcgui.ListItem(path=playback_url)
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), False, item)
    xbmc.Player().play(playback_url)
