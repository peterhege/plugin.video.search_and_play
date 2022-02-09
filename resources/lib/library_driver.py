# -*- coding: utf-8 -*-

import json
import time

import xbmc
import xbmcgui


def search_movie(tmdb_data, properties=None):
    try:
        if properties is None:
            properties = ['title', 'resume', 'originaltitle']
        query = {"jsonrpc": "2.0", "method": 'VideoLibrary.GetMovies', "params": {
            "properties": properties,
            "sort": {"method": 'title'},
            "filter": {"field": "title", "operator": "contains", "value": tmdb_data['title']},
        }, "id": 1}
        response = json.loads(unicode(xbmc.executeJSONRPC(json.dumps(query)), 'utf-8', errors='ignore'))
        if 'error' in response:
            xbmcgui.Dialog().notification('Hiba {}'.format(response['error']['code']), response['error']['message'],
                                          xbmcgui.NOTIFICATION_ERROR)
            return None

        if not response['result']:
            return None

        for movie in response['result']['movies']:
            if movie['title'] == tmdb_data['title'] or movie['originaltitle'] == tmdb_data['original_title']:
                return movie
        return None
    except Exception as e:
        xbmc.log(e.message, xbmc.LOGWARNING)
        return None
    except:
        return None


def context(library_data):
    context_menu = {}
    context_play = 'library_driver.play({id})'.format(id=library_data['movieid'])
    context_menu[context_play] = 'Lejátszás Médiatárból'

    resume = int(library_data['resume']['position'])
    if resume > 0:
        m, s = divmod(resume, 60)
        h, m = divmod(m, 60)
        context_resume = 'library_driver.play({id},{resume})'.format(id=library_data['movieid'], resume=resume)
        context_menu[context_resume] = 'Folytatás innen: {time}'.format(time=('%d:%02d:%02d' % (h, m, s)))

    return context_menu


def play(movie_id, resume=None):
    query = {"jsonrpc": "2.0", "method": "Player.Open", "params": {"item": {"movieid": int(movie_id)}}, "id": 1}
    try:
        response = json.loads(unicode(xbmc.executeJSONRPC(json.dumps(query)), 'utf-8', errors='ignore'))
        if 'error' in response:
            xbmcgui.Dialog().notification('Hiba {}'.format(response['error']['code']), response['error']['message'],
                                          xbmcgui.NOTIFICATION_ERROR)
        xbmc.log(str(response), xbmc.LOGERROR)
        if resume:
            time.sleep(.5)
            query = {"jsonrpc": "2.0", "method": "Player.Seek",
                     "params": {"playerid": 1, "value": {"seconds": int(resume)}}, "id": 1}
            response = json.loads(unicode(xbmc.executeJSONRPC(json.dumps(query)), 'utf-8', errors='ignore'))
            if 'error' in response:
                xbmcgui.Dialog().notification('Hiba {}'.format(response['error']['code']), response['error']['message'],
                                              xbmcgui.NOTIFICATION_ERROR)
                xbmc.log(str(response), xbmc.LOGERROR)
    except Exception as e:
        xbmcgui.Dialog().notification('Error', e.message, xbmcgui.NOTIFICATION_ERROR)
    except:
        xbmcgui.Dialog().notification('Error', 'Ismeretlen hiba', xbmcgui.NOTIFICATION_ERROR)


class MyPlayer(xbmc.Player):
    def __init__(self, *args, **kwargs):
        xbmc.Player.__init__(self)
        self.resume = 0

    def onAVStarted(self):
        if self.resume > 0:
            self.seekTime(float(self.resume))