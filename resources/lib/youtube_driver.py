# -*- coding: utf-8 -*-
import xbmc
import xbmcgui
import xbmcplugin

try:
    sys
except:
    import sys


def for_movie(tmdb_data):
    videos = []
    for video in tmdb_data['videos']:
        if video['site'] == 'YouTube':
            videos.append(video)
    return videos


def context(videos):
    if type(videos) != list:
        return {}
    context_menu = {}
    for video in videos:
        context_play = 'youtube_driver.play({key})'.format(key=video['key'])
        context_menu[context_play] = video['name']
        if video['type'] == 'Trailer':
            context_menu[context_play] += ' (Előzetes)'
    return context_menu


def play(key):
    playback_url = 'plugin://plugin.video.youtube/?action=play_video&videoid={key}'.format(key=key)
    item = xbmcgui.ListItem(path=playback_url)
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), False, item)
    xbmc.Player().play(playback_url)
