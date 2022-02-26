# -*- coding: utf-8 -*-
import base64
import json
import re
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import tmdbsimple as tmdb

from resources.lib import movies
from resources.lib.control import get_media, build_query, dialog, setting
from resources.lib.tmdb.find import Trending

try:
    sys
except:
    import sys

__addon__ = xbmcaddon.Addon()
__addon_name__ = __addon__.getAddonInfo('name')
__TMDB_IMAGE_BASE__ = 'https://image.tmdb.org/t/p/original'

tmdb.API_KEY = setting('tmdb_key')
if not tmdb.API_KEY:
    tmdb.API_KEY = dialog.input('The Movie DB API kulcs')
    setting('tmdb_key', tmdb.API_KEY)
    if not tmdb.API_KEY:
        sys.exit()


def main_folders():
    add_dir('Filmek', 'movie_folder', 'movie_icon.png', 'movie_fanart.jpg', 'Filmek keresése', 1)
    add_dir('Sorozatok', 'tv_folder', 'tv_icon.png', 'tv_fanart.jpg', 'Filmek keresése', 1)


def movie_folder():
    add_dir('Keresés kifejezés alapján', 'movie_search', 'search_icon.png', 'movie_fanart.jpg', 'Keresés', 1)
    add_dir('Részletes keresés', 'movie_discover', 'search_icon.png', 'movie_fanart.jpg', 'Keresés', 1)
    add_dir('Trendi', 'movie_trending', 'search_icon.png', 'movie_fanart.jpg', 'Trendi filmek', 1)


def tv_folder():
    pass


def movie_trending():
    try:
        movies = Trending(media_type='movie', time_window='week').info(language=xbmc.getLanguage(xbmc.ISO_639_1))
    except Exception as e:
        dialog.ok('error', e.message)
    xbmc.log(json.dumps(movies), xbmc.LOGERROR)
    for movie in movies['results']:
        add_dir(
            movie['title'].encode('utf-8'), 'load_movie', '{}/{}'.format(__TMDB_IMAGE_BASE__, movie['poster_path']),
            '{}/{}'.format(__TMDB_IMAGE_BASE__, movie['backdrop_path']), movie['overview'].encode('utf-8'), '1',
            movie['id'], True
        )
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')


def movie_search():
    menu = [
        {'name': 'Kifejezés', 'key': 'query'},
        {'name': 'Felnőtt tartalom', 'key': 'include_adult', 'value': False, 'type': bool},
        {'name': 'Év', 'key': 'year', 'type': xbmcgui.INPUT_NUMERIC, 'valid': r'[1-2][09][0-9]{2}'},
        {'name': 'Keresés indítása', 'key': 'search'}
    ]
    search_params = get_search_params(menu, ['Kifejezés'])
    if not search_params:
        return
    movie_list('Search', search_params)


def movie_discover():
    menu = [
        {'name': 'Évtől', 'key': 'release_date.gte', 'type': xbmcgui.INPUT_NUMERIC, 'valid': r'[1-2][09][0-9]{2}'},
        {'name': 'Évig', 'key': 'release_date.lte', 'type': xbmcgui.INPUT_NUMERIC, 'valid': r'[1-2][09][0-9]{2}'},
        {'name': 'Év', 'key': 'year', 'type': xbmcgui.INPUT_NUMERIC, 'valid': r'[1-2][09][0-9]{2}'},
        {'name': 'Felnőtt tartalom', 'key': 'include_adult', 'value': False, 'type': bool},
        {'name': 'Keresés indítása', 'key': 'search'}
    ]
    search_params = get_search_params(menu, [])
    if 'release_date.lte' in search_params and 'release_date.gte' in search_params \
            and search_params['release_date.gte'] > search_params['release_date.lte']:
        (search_params['release_date.gte'], search_params['release_date.lte']) = (
            search_params['release_date.lte'], search_params['release_date.gte'])
    if 'release_date.gte' in search_params:
        search_params['release_date.gte'] = '{year}-01-01'.format(year=search_params['release_date.gte'])
    if 'release_date.lte' in search_params:
        search_params['release_date.lte'] = '{year}-12-31'.format(year=search_params['release_date.lte'])
    if type(search_params) != dict:
        return
    movie_list('Discover', search_params)


def get_search_params(menu, required):
    for m in menu:
        if 'type' not in m:
            m['type'] = xbmcgui.INPUT_ALPHANUM
    while True:
        context_menu = []
        for m in menu:
            name = m['name']
            if 'value' in m:
                value = m['value']
                if m['type'] == bool:
                    value = 'Igen' if m['value'] else 'Nem'
                name += ': {}'.format(value)
            context_menu.append(name)

        menu_index = dialog.contextmenu(context_menu)
        if menu_index == -1:
            sys.exit()
        selected = menu[menu_index]
        if selected['key'] == 'search':
            if len(required):
                dialog.ok('Hiba', 'A következő mezők megadása kötelező: {req}'.format(req=', '.join(required)))
            else:
                break
        elif selected['type'] == bool:
            selected['value'] = bool(dialog.yesno(selected['name'], '{} bekapcsolva?'.format(menu[menu_index]['name'])))
        else:
            valid = False
            while not valid:
                selected['value'] = dialog.input(selected['name'], type=selected['type'])
                if not selected['value']:
                    del selected['value']
                    break
                valid = True if 'valid' not in selected else re.match(selected['valid'], selected['value'])
                if not valid:
                    dialog.notification('Hiba', 'A megadott érték érvénytelen', xbmcgui.NOTIFICATION_WARNING)
            if valid and selected['name'] in required:
                required.remove(selected['name'])

    search_params = {}
    for m in menu:
        if 'value' not in m or m['key'] == 'search':
            continue
        search_params[m['key']] = m['value']
    search_params['language'] = xbmc.getLanguage(xbmc.ISO_639_1)
    return search_params


def movie_list(engine_name=None, search_params=None):
    if engine_name is None:
        data = json.loads(base64.b64decode(params['data']))
        search_params = data['search_params']
        engine_name = data['engine']
    engine = eval('tmdb.{}()'.format(engine_name))
    search_params['page'] = int(params['page'])
    try:
        movies = engine.movie(**search_params)
    except Exception as e:
        dialog.ok('Hiba', e.message)
        return
    for movie in movies['results']:
        if not movie['poster_path']:
            continue
        add_dir(
            '{title} ({year})'.format(title=movie['title'].encode('utf-8'), year=movie['release_date'][:4]),
            'load_movie', '{}/{}'.format(__TMDB_IMAGE_BASE__, movie['poster_path']),
            '{}/{}'.format(__TMDB_IMAGE_BASE__, movie['backdrop_path']), movie['overview'].encode('utf-8'), '1',
            movie['id'], True
        )
    if int(params['page']) < int(movies['total_pages']):
        add_dir(
            name='Következő oldal',
            method='movie_list',
            icon='a',
            fanart='a',
            description=str(int(params['page']) + 1),
            page=str(int(params['page']) + 1),
            data=base64.b64encode(json.dumps({'engine': engine_name, 'search_params': search_params}))
        )
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')


def load_movie():
    movie_id = int(params['data'])
    movies.load_movie(movie_id)


def add_dir(name, method, icon, fanart, description, page, data=None, is_playable=False):
    icon = icon if re.match(r'^http(s)?:\/\/.*', icon) else get_media(icon)
    fanart = fanart if re.match(r'^http(s)?:\/\/.*', fanart) else get_media(fanart)
    data = str({}) if data is None else data
    query = {'method': method, 'data': data, 'page': page}
    url = "{base}?{query}".format(base=sys.argv[0], query=build_query(query))
    list_item = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
    list_item.setInfo(type="Video", infoLabels={"Title": name, "Plot": description})
    list_item.setProperty("Fanart_Image", fanart)
    if is_playable:
        list_item.setProperty('IsPlayable', 'true')
        list_item.setProperty('isFolder', 'false')
        list_item.setContentLookup(False)
        list_item.setArt({'icon': icon, 'thumb': icon, 'poster': icon, 'fanart': fanart})
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=list_item, isFolder=True)


def get_params():
    list_of_params = {}
    param_str = sys.argv[2]
    if len(param_str) >= 2:
        argv_params = sys.argv[2]
        cleaned_params = argv_params.replace('?', '')
        pairs_of_params = cleaned_params.split('&')
        for i in range(len(pairs_of_params)):
            slices = pairs_of_params[i].split('=')
            if (len(slices)) == 2:
                list_of_params[slices[0]] = slices[1]
    return list_of_params


params = get_params()

try:
    method = params["method"]
    locals()[method]()
except:
    method = None
    main_folders()

if method not in ['load_movie']:
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
