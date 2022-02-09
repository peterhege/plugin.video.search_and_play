# -*- coding: utf-8 -*-
import re
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import tmdbsimple as tmdb

from resources.lib import library_driver, youtube_driver, netflix_driver
from resources.lib.control import get_media, build_query, dialog, setting, call_user_func

try:
    sys
except:
    import sys

__addon__ = xbmcaddon.Addon()
__addon_name__ = __addon__.getAddonInfo('name')
__TMDB_IMAGE_BASE__ = 'https://image.tmdb.org/t/p/original'

tmdb.API_KEY = setting('tmdb_key')
while not tmdb.API_KEY:
    tmdb.API_KEY = dialog.input('The Movie DB API kulcs')
    setting('tmdb_key', tmdb.API_KEY)


def main_folders():
    add_dir('Filmek', 'movie_folder', 'movie_icon.png', 'movie_fanart.jpg', 'Filmek keresése', 1)
    add_dir('Sorozatok', 'tv_folder', 'tv_icon.png', 'tv_fanart.jpg', 'Filmek keresése', 1)


def movie_folder():
    add_dir('Keresés', 'movie_search', 'search_icon.png', 'movie_fanart.jpg', 'Keresés', 1)


def tv_folder():
    pass


def movie_search():
    menu = [
        {'name': 'Kifejezés', 'key': 'query'},
        {'name': 'Felnőtt tartalom', 'key': 'include_adult', 'value': False, 'type': bool},
        {'name': 'Keresés indítása', 'key': 'search'}
    ]
    for m in menu:
        if 'type' not in m:
            m['type'] = xbmcgui.INPUT_ALPHANUM
    while True:
        context = []
        for m in menu:
            name = m['name']
            if 'value' in m:
                value = m['value']
                if m['type'] == bool:
                    value = 'Igen' if m['value'] else 'Nem'
                name += ': {}'.format(value)
            context.append(name)

        menu_index = dialog.contextmenu(context)
        selected = menu[menu_index]
        if selected['key'] == 'search':
            break
        if selected['type'] == bool:
            selected['value'] = bool(dialog.yesno(selected['name'], '{} bekapcsolva?'.format(menu[menu_index]['name'])))
        else:
            selected['value'] = dialog.input(selected['name'], type=selected['type'])

    search_params = {}
    for m in menu:
        if 'value' not in m or m['key'] == 'search':
            continue
        search_params[m['key']] = m['value']
    search_params['language'] = xbmc.getLanguage(xbmc.ISO_639_1)
    movie_list(search_params)


def movie_list(search_params=None):
    search = tmdb.Search()
    movies = search.movie(**search_params)
    for movie in movies['results']:
        add_dir(
            movie['title'].encode('utf-8'), 'load_movie', '{}/{}'.format(__TMDB_IMAGE_BASE__, movie['poster_path']),
            '{}/{}'.format(__TMDB_IMAGE_BASE__, movie['backdrop_path']), movie['overview'].encode('utf-8'), '1',
            movie['id'], True
        )
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')


def load_movie():
    movie = tmdb.Movies(int(params['data']))
    data = movie.info(language=xbmc.getLanguage(xbmc.ISO_639_1))
    videos = movie.videos(language=xbmc.getLanguage(xbmc.ISO_639_1))
    data['videos'] = videos['results'] if 'results' in videos else []
    context_menu = {}
    for driver in [library_driver, youtube_driver, netflix_driver]:
        found = driver.search_movie(data)
        if found:
            context_menu.update(driver.context(found))
    selected_menu = dialog.contextmenu(context_menu.values())
    if selected_menu > -1:
        callable_name = context_menu.keys()[selected_menu]
        call_user_func(callable_name)


def add_dir(name, method, icon, fanart, description, page, data=None, is_playable=False):
    icon = icon if re.match(r'^http(s)?:\/\/', icon) else get_media(icon)
    fanart = fanart if re.match(r'^http(s)?:\/\/', fanart) else get_media(fanart)
    data = str({}) if data is None else data
    query = {
        'method': method, 'data': data,
        # 'name': name,  'icon': icon,
        # 'fanart': fanart, 'description': description, 'page': page
    }
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
