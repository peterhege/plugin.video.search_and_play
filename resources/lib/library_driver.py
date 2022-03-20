# -*- coding: utf-8 -*-

import json
import time

import xbmc
import xbmcgui


def for_movie(tmdb_data, properties=None):
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


def for_tv(tmdb_data, properties=None):
    try:
        if properties is None:
            properties = ['title', 'watchedepisodes', 'originaltitle']
        query = {"jsonrpc": "2.0", "method": 'VideoLibrary.GetTVShows', "params": {
            "properties": properties,
            "sort": {"method": 'title'},
            "filter": {"field": "title", "operator": "contains", "value": tmdb_data['name']},
        }, "id": 1}
        response = json.loads(unicode(xbmc.executeJSONRPC(json.dumps(query)), 'utf-8', errors='ignore'))
        if 'error' in response:
            xbmcgui.Dialog().notification('Hiba {}'.format(response['error']['code']), response['error']['message'],
                                          xbmcgui.NOTIFICATION_ERROR)
            return None

        if not response['result']:
            return None

        for tv in response['result']['tvshows']:
            if tv['title'] == tmdb_data['name'] or tv['originaltitle'] == tmdb_data['original_name']:
                tv['episodes'] = get_episodes(tv['tvshowid'])
                return tv
        return None

    except Exception as e:
        xbmc.log(e.message, xbmc.LOGWARNING)
        return None
    except:
        return None


def get_episodes(tv_id, properties=None):
    try:
        if properties is None:
            properties = ['title', 'resume', 'originaltitle', 'season', 'episode']
        query = {"jsonrpc": "2.0", "method": 'VideoLibrary.GetEpisodes', "params": {
            'tvshowid': tv_id,
            "properties": properties
        }, "id": 1}

        response = json.loads(unicode(xbmc.executeJSONRPC(json.dumps(query)), 'utf-8', errors='ignore'))

        if 'error' in response:
            xbmcgui.Dialog().notification('Hiba {}'.format(response['error']['code']), response['error']['message'],
                                          xbmcgui.NOTIFICATION_ERROR)
            return None

        if not response['result']:
            return None

        return response['result']['episodes']
    except Exception as e:
        xbmc.log(e.message, xbmc.LOGWARNING)
        return None


def find_movie_by_path(path):
    query = {"jsonrpc": "2.0", "method": 'VideoLibrary.GetMovies', "params": {
        "properties": ['title', 'resume', 'originaltitle', 'file', 'imdbnumber'],
        "sort": {"method": 'title'},
        "filter": {"field": "path", "operator": "contains", "value": path},
    }, "id": 1}

    response = json.loads(unicode(xbmc.executeJSONRPC(json.dumps(query)), 'utf-8', errors='ignore'))
    if 'error' in response:
        xbmcgui.Dialog().notification('Hiba {}'.format(response['error']['code']), response['error']['message'],
                                      xbmcgui.NOTIFICATION_ERROR)
        return None

    if not response['result']:
        return None

    return response


def remove_movie(movie_id):
    query = {"jsonrpc": "2.0", "method": 'VideoLibrary.RemoveMovie', "params": {
        "movieid": movie_id
    }, "id": 1}

    response = json.loads(unicode(xbmc.executeJSONRPC(json.dumps(query)), 'utf-8', errors='ignore'))
    if 'error' in response:
        xbmcgui.Dialog().notification('Hiba {}'.format(response['error']['code']), response['error']['message'],
                                      xbmcgui.NOTIFICATION_ERROR)
        return None

    if not response['result']:
        return None

    return response


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


def context_tv(library_data):
    first_episode = library_data['episodes'][0]
    watched = int(library_data['watchedepisodes'])
    next_episode = library_data['episodes'][watched] if watched else None

    context_menu = {}
    context_play = 'library_driver.play_tv({id})'.format(id=first_episode['episodeid'])
    context_menu[context_play] = 'Lejátszás ({} - S{}E{})'.format(
        first_episode['title'].encode('utf-8'),
        first_episode['season'],
        first_episode['episode']
    )
    if next_episode:
        resume = int(next_episode['resume']['position'])
        if resume > 0:
            context_play = 'library_driver.play_tv({id},{resume})'.format(id=next_episode['episodeid'], resume=resume)
        else:
            context_play = 'library_driver.play_tv({id})'.format(id=next_episode['episodeid'])
        context_menu[context_play] = 'Folytatás ({} - S{}E{})'.format(
            next_episode['title'].encode('utf-8'),
            next_episode['season'],
            next_episode['episode']
        )

    return context_menu


def tv_shows(tv_id):
    pass


def play(movie_id, resume=None):
    xbmc.executebuiltin('Dialog.Close(all,true)')
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


def play_tv(tv_id, resume=None):
    xbmc.executebuiltin('Dialog.Close(all,true)')
    query = {"jsonrpc": "2.0", "method": "Player.Open", "params": {"item": {"episodeid": int(tv_id)}}, "id": 1}
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


def update_library():
    query = {"jsonrpc": "2.0", "method": "VideoLibrary.Scan", "params": {"showdialogs": False}, "id": 1}
    return json.loads(unicode(xbmc.executeJSONRPC(json.dumps(query)), 'utf-8', errors='ignore'))
