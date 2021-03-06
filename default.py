# -*- coding: utf-8 -*-
import base64
import hashlib
import json
import random
import re
import urllib
import datetime
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import tmdbsimple as tmdb

from resources.lib.tmdb.find import Trending
from resources.lib import movies, library_driver, tvs
from resources.lib.control import get_media, build_query, dialog, setting

try:
    sys
except:
    import sys

KODI_SORT_METHOD_NAME = 1
KODI_SORT_METHOD_DATE = 2
KODI_SORT_METHOD_SIZE = 3
KODI_SORT_METHOD_FILE = 4
KODI_SORT_METHOD_PATH = 5
KODI_SORT_METHOD_DRIVETYPE = 6
KODI_SORT_METHOD_TITLE = 7
KODI_SORT_METHOD_TRACKNUMBER = 8
KODI_SORT_METHOD_TIME = 9
KODI_SORT_METHOD_ARTIST = 10
KODI_SORT_METHOD_ARTISTTHENYEAR = 11
KODI_SORT_METHOD_ALBUM = 12
KODI_SORT_METHOD_ALBUMTYPE = 13
KODI_SORT_METHOD_GENRE = 14
KODI_SORT_METHOD_COUNTRY = 15
KODI_SORT_METHOD_YEAR = 16
KODI_SORT_METHOD_RATING = 17
KODI_SORT_METHOD_USERRATING = 18
KODI_SORT_METHOD_VOTES = 19
KODI_SORT_METHOD_TOP250 = 20
KODI_SORT_METHOD_PROGRAMCOUNT = 21
KODI_SORT_METHOD_PLAYLISTORDER = 22
KODI_SORT_METHOD_EPISODENUMBER = 23
KODI_SORT_METHOD_SEASON = 24
KODI_SORT_METHOD_NUMBEROFEPISODES = 25
KODI_SORT_METHOD_NUMBEROFWATCHEDEPISODES = 26
KODI_SORT_METHOD_TVSHOWSTATUS = 27
KODI_SORT_METHOD_TVSHOWTITLE = 28
KODI_SORT_METHOD_SORTTITLE = 29
KODI_SORT_METHOD_PRODUCTIONCODE = 30
KODI_SORT_METHOD_MPAA = 31
KODI_SORT_METHOD_VIDEORESOLUTION = 32
KODI_SORT_METHOD_VIDEOCODEC = 33
KODI_SORT_METHOD_VIDEOASPECTRATIO = 34
KODI_SORT_METHOD_AUDIOCHANNELS = 35
KODI_SORT_METHOD_AUDIOCODEC = 36
KODI_SORT_METHOD_AUDIOLANGUAGE = 37
KODI_SORT_METHOD_SUBTITLELANGUAGE = 38
KODI_SORT_METHOD_STUDIO = 39
KODI_SORT_METHOD_DATEADDED = 40
KODI_SORT_METHOD_LASTPLAYED = 41
KODI_SORT_METHOD_PLAYCOUNT = 42
KODI_SORT_METHOD_LISTENERS = 43
KODI_SORT_METHOD_BITRATE = 44
KODI_SORT_METHOD_RANDOM = 45
KODI_SORT_METHOD_CHANNEL = 46
KODI_SORT_METHOD_CHANNELNUMBER = 47
KODI_SORT_METHOD_DATETAKEN = 48
KODI_SORT_METHOD_RELEVANCE = 49
KODI_SORT_METHOD_INSTALLDATE = 50
KODI_SORT_METHOD_LASTUPDATED = 51
KODI_SORT_METHOD_LASTUSED = 52

__addon__ = xbmcaddon.Addon()
__addon_name__ = __addon__.getAddonInfo('name')
__TMDB_IMAGE_BASE__ = 'https://image.tmdb.org/t/p/original'
__GENRES__ = None
__TV_GENRES__ = None
__SORT__ = {
    'movie': {
        'Discover': {
            'popularity.asc': {'name': 'N??pszer??tlen', 'kodi': KODI_SORT_METHOD_RATING},
            'popularity.desc': {'name': 'N??pszer??', 'kodi': KODI_SORT_METHOD_RATING},
            'primary_release_date.asc': {'name': 'Megjelen??s szerint n??vekv??', 'kodi': KODI_SORT_METHOD_YEAR},
            'primary_release_date.desc': {'name': 'Megjelen??s szerint cs??kken??', 'kodi': KODI_SORT_METHOD_YEAR},
            'original_title.asc': {'name': 'Eredeti c??m szerint n??vekv??', 'kodi': KODI_SORT_METHOD_TITLE},
            'original_title.desc': {'name': 'Eredeti c??m szerint cs??kken??', 'kodi': KODI_SORT_METHOD_TITLE},
            'vote_average.asc': {'name': '??rt??kel??s szerint n??vekv??', 'kodi': KODI_SORT_METHOD_RATING},
            'vote_average.desc': {'name': '??rt??kel??s szerint cs??kken??', 'kodi': KODI_SORT_METHOD_RATING}
        }
    },
    'tv': {}
}

tmdb.API_KEY = setting('tmdb_key')
if not tmdb.API_KEY:
    tmdb.API_KEY = dialog.input('The Movie DB API kulcs')
    setting('tmdb_key', tmdb.API_KEY)
    if not tmdb.API_KEY:
        sys.exit()

if not __GENRES__:
    genres = tmdb.genres.Genres().movie_list(language=xbmc.getLanguage(xbmc.ISO_639_1))
    __GENRES__ = {}
    for genre in genres['genres']:
        __GENRES__[genre['id']] = genre['name'].encode('utf-8')

if not __TV_GENRES__:
    genres = tmdb.genres.Genres().tv_list(language=xbmc.getLanguage(xbmc.ISO_639_1))
    __TV_GENRES__ = {}
    for genre in genres['genres']:
        __TV_GENRES__[genre['id']] = genre['name'].encode('utf-8')


def main_folders():
    add_dir('Filmek', 'movie_folder', 'movie_icon.png', 'movie_fanart.jpg', 'Filmek keres??se', 1)
    add_dir('Sorozatok', 'tv_folder', 'tv_icon.png', 'tv_fanart.jpg', 'Filmek keres??se', 1)


def movie_folder():
    add_dir('V??letlenszer??', 'movie_random', 'search_icon.png', 'movie_fanart.jpg', 'Keres??s', 1)
    add_dir('Keres??s kifejez??s alapj??n', 'movie_search', 'search_icon.png', 'movie_fanart.jpg', 'Keres??s', 1)
    add_dir('R??szletes keres??s', 'movie_discover', 'search_icon.png', 'movie_fanart.jpg', 'Keres??s', 1)
    add_dir('Trendi', 'movie_trending', 'search_icon.png', 'movie_fanart.jpg', 'Trendi filmek', 1)


def tv_folder():
    add_dir('Keres??s kifejez??s alapj??n', 'tv_search', 'search_icon.png', 'tv_fanart.jpg', 'Keres??s', 1)


def tv_search():
    menu = [
        {'name': 'Kifejez??s', 'key': 'query'},
        {'name': 'Feln??tt tartalom', 'key': 'include_adult', 'value': False, 'type': bool},
        {'name': 'Megjelen??s ??ve', 'key': 'first_air_date_year', 'type': xbmcgui.INPUT_NUMERIC,
         'valid': r'[12][09][0-9]{2}'},
        {'name': 'Keres??s ind??t??sa', 'key': 'search'}
    ]
    search_params = get_search_params(menu, ['Kifejez??s'])
    if not search_params:
        return
    tv_list('Search', search_params)


def movie_random():
    search_params = json.loads(base64.b64decode(params['data'])) if 'data' in params and params[
        'data'] != '{}' else None

    if not search_params:
        menu = [
            {'name': '??vt??l', 'key': 'year.gte', 'type': xbmcgui.INPUT_NUMERIC, 'valid': r'[1-2][09][0-9]{2}',
             'value': 2000},
            {'name': '??vig', 'key': 'year.lte', 'type': xbmcgui.INPUT_NUMERIC, 'valid': r'[1-2][09][0-9]{2}',
             'value': datetime.datetime.now().strftime('%Y')},
            {'name': 'Min ??rt??kel??s', 'key': 'vote_average.gte', 'type': xbmcgui.INPUT_NUMERIC,
             'valid': r'([0-9](\.[0-9]+)?|10)', 'value': 6},
            {'name': 'Feln??tt tartalom', 'key': 'include_adult', 'value': False, 'type': bool},
            {'name': 'Keres??s ind??t??sa', 'key': 'search'}
        ]

        search_params = get_search_params(menu, [])

    search_params['vote_count.gte'] = 1000

    (year_gte, year_lte) = (search_params['year.gte'], search_params['year.lte'])
    del search_params['year.gte'], search_params['year.lte']

    movies = {}
    attempt = 0
    results = {}
    while len(movies.values()) < 10 and attempt < 100:
        search_params['primary_release_year'] = str(random.randint(int(year_gte), int(year_lte)))
        search_key = hashlib.md5(json.dumps(search_params)).hexdigest()
        if search_key not in results:
            results[search_key] = tmdb.Discover().movie(**search_params)
        result = results[search_key]

        pages = int(result['total_pages'])
        search_params['page'] = random.randint(1, pages)
        search_key = hashlib.md5(json.dumps(search_params)).hexdigest()
        if search_key not in results:
            results[search_key] = tmdb.Discover().movie(**search_params)
        result = results[search_key]

        movie = random.choice(result['results'])

        if movie['id'] not in movies:
            movies[movie['id']] = movie

        search_params['page'] = 1

        attempt += 1

        if attempt > 50:
            search_params['vote_count.gte'] = 100
        elif attempt > 90:
            search_params['vote_count.gte'] = 1

    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_DATE)
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_YEAR)
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_TITLE)
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_RATING)
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_GENRE)

    show_movies(movies.values())

    search_params['year.gte'] = year_gte
    search_params['year.lte'] = year_lte
    add_dir('??jra', 'movie_random', 'search_icon.png', 'movie_fanart.jpg', '??j lista gener??l??sa', 1,
            data=base64.b64encode(json.dumps(search_params)), position='bottom')


def movie_trending():
    movie_list('Trending', {'language': xbmc.getLanguage(xbmc.ISO_639_1)})


def movie_search():
    menu = [
        {'name': 'Kifejez??s', 'key': 'query'},
        {'name': 'Feln??tt tartalom', 'key': 'include_adult', 'value': False, 'type': bool},
        {'name': '??v', 'key': 'primary_release_year', 'type': xbmcgui.INPUT_NUMERIC, 'valid': r'[12][09][0-9]{2}'},
        {'name': 'Keres??s ind??t??sa', 'key': 'search'}
    ]
    search_params = get_search_params(menu, ['Kifejez??s'])
    if not search_params:
        return
    movie_list('Search', search_params)


def movie_discover():
    menu = [
        {'name': '??vt??l', 'key': 'primary_release_date.gte', 'type': xbmcgui.INPUT_NUMERIC,
         'valid': r'[1-2][09][0-9]{2}'},
        {'name': '??vig', 'key': 'primary_release_date.lte', 'type': xbmcgui.INPUT_NUMERIC,
         'valid': r'[1-2][09][0-9]{2}'},
        {'name': '??v', 'key': 'primary_release_year', 'type': xbmcgui.INPUT_NUMERIC, 'valid': r'[1-2][09][0-9]{2}'},
        {'name': 'Min ??rt??kel??s', 'key': 'vote_average.gte', 'type': xbmcgui.INPUT_NUMERIC,
         'valid': r'([0-9](\.[0-9]+)?|10)', 'value': 6},
        {'name': 'Min ??rt??kel??s sz??m', 'key': 'vote_count.gte', 'type': xbmcgui.INPUT_NUMERIC, 'value': 500},
        {'name': 'Feln??tt tartalom', 'key': 'include_adult', 'value': False, 'type': bool},
        {'name': 'Keres??s ind??t??sa', 'key': 'search'}
    ]
    search_params = get_search_params(menu, [])

    if type(search_params) != dict:
        return

    search_params['sort_by'] = 'popularity.desc'

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
                dialog.ok('Hiba', 'A k??vetkez?? mez??k megad??sa k??telez??: {req}'.format(req=', '.join(required)))
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
                    dialog.notification('Hiba', 'A megadott ??rt??k ??rv??nytelen', xbmcgui.NOTIFICATION_WARNING)
            if valid and selected['name'] in required:
                required.remove(selected['name'])

    search_params = {}
    for m in menu:
        if 'value' not in m or m['key'] == 'search':
            continue
        search_params[m['key']] = m['value']
    search_params['language'] = xbmc.getLanguage(xbmc.ISO_639_1)
    if 'primary_release_date.gte' in search_params:
        search_params['primary_release_date.gte'] = datetime.datetime(
            int(search_params['primary_release_date.gte']) - 1, 12,
            31, 23, 59, 59).isoformat()
    if 'primary_release_date.lte' in search_params:
        search_params['primary_release_date.lte'] = datetime.datetime(
            int(search_params['primary_release_date.lte']) + 1, 1,
            1, 0, 0, 0).isoformat()
    return search_params


def movie_list(engine_name=None, search_params=None, start_page=1):
    if engine_name is None:
        data = json.loads(base64.b64decode(params['data']))
        search_params = data['search_params']
        engine_name = data['engine']
        start_page = data['page']

    imported_engines = [Trending.__name__]

    try:
        engine = eval('{}()'.format(engine_name)) if engine_name in imported_engines else eval(
            'tmdb.{}()'.format(engine_name))
    except Exception as e:
        dialog.ok('Hiba', e.message)
        return

    if 'page' not in search_params:
        search_params['page'] = int(params['page'])

    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    if engine_name != 'Trending':
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_DATE)
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_YEAR)
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_TITLE)
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_RATING)
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_GENRE)

    try:
        movies = engine.movie(**search_params)
    except Exception as e:
        dialog.ok('Hiba', e.message)
        return

    show_movies(movies['results'])

    if search_params['page'] < int(movies['total_pages']):
        search_params['page'] += 1
        max_page_per_view = 20
        if search_params['page'] - start_page == max_page_per_view:
            if engine_name in __SORT__['movie']:
                add_dir(
                    name='Rendez??s',
                    method='movie_sort_by',
                    icon='sort_icon.png',
                    fanart='sort_icon.png',
                    description=__SORT__['movie'][engine_name][
                        search_params['sort_by']]['name'] if 'sort_by' in search_params and engine_name in __SORT__[
                        'movie'] else 'Alap??rtelmezett',
                    page='1',
                    data=base64.b64encode(
                        json.dumps({'engine': engine_name, 'search_params': search_params})),
                    position='top'
                )

            add_dir(
                name='K??vetkez?? oldal',
                method='movie_list',
                icon='a',
                fanart='a',
                description='{}/{}'.format(search_params['page'] / max_page_per_view,
                                           int(movies['total_pages']) / max_page_per_view),
                page=str(int(params['page']) + 1),
                data=base64.b64encode(
                    json.dumps({'engine': engine_name, 'search_params': search_params, 'page': search_params['page']})),
                position='bottom'
            )
            finalise('movie_list', engine_name)
        else:
            movie_list(engine_name, search_params, start_page)


def tv_list(engine_name=None, search_params=None, start_page=1):
    if engine_name is None:
        data = json.loads(base64.b64decode(params['data']))
        search_params = data['search_params']
        engine_name = data['engine']
        start_page = data['page']

    imported_engines = [Trending.__name__]

    try:
        engine = eval('{}()'.format(engine_name)) if engine_name in imported_engines else eval(
            'tmdb.{}()'.format(engine_name))
    except Exception as e:
        dialog.ok('Hiba', e.message)
        return

    if 'page' not in search_params:
        search_params['page'] = int(params['page'])

    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    if engine_name != 'Trending':
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_DATE)
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_YEAR)
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_TITLE)
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_RATING)
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_GENRE)

    try:
        tvs = engine.tv(**search_params)
    except Exception as e:
        dialog.ok('Hiba', e.message)
        return

    show_tvs(tvs['results'])

    if search_params['page'] < int(tvs['total_pages']):
        search_params['page'] += 1
        max_page_per_view = 20
        if search_params['page'] - start_page == max_page_per_view:
            if engine_name in __SORT__['tv']:
                add_dir(
                    name='Rendez??s',
                    method='tv_sort_by',
                    icon='sort_icon.png',
                    fanart='sort_icon.png',
                    description=__SORT__['tv'][engine_name][
                        search_params['sort_by']]['name'] if 'sort_by' in search_params and engine_name in __SORT__[
                        'tv'] else 'Alap??rtelmezett',
                    page='1',
                    data=base64.b64encode(
                        json.dumps({'engine': engine_name, 'search_params': search_params})),
                    position='top'
                )

            add_dir(
                name='K??vetkez?? oldal',
                method='tv_list',
                icon='a',
                fanart='a',
                description='{}/{}'.format(search_params['page'] / max_page_per_view,
                                           int(tvs['total_pages']) / max_page_per_view),
                page=str(int(params['page']) + 1),
                data=base64.b64encode(
                    json.dumps({'engine': engine_name, 'search_params': search_params, 'page': search_params['page']})),
                position='bottom'
            )
            finalise('tv_list', engine_name)
        else:
            tv_list(engine_name, search_params, start_page)


def show_movies(movies):
    for movie in movies:
        if not movie['poster_path']:
            continue

        info = {
            'title': movie['title'].encode('utf-8'),
            'plot': '[B]??rt??kel??s: {}[/B] '.format(movie['vote_average'] if 'vote_average' in movie else 0) + (
                movie['overview'].encode('utf-8') if 'overview' in movie else ''),
            'originaltitle': movie['original_title'].encode('utf-8') if 'original_title' in movie else '',
            'genre': [__GENRES__[genre_id] for genre_id in movie['genre_ids']] if 'genre_ids' in movie else 'Egy??b',
            'rating': movie['vote_average'] if 'vote_average' in movie else 0
        }

        if 'release_date' in movie:
            release = movie['release_date'].split('-')
            if len(release) == 3 and int(release[0]) >= 1900:
                release = datetime.datetime(int(release[0]), int(release[1]), int(release[2]))
                info['date'] = release.strftime('%d.%m.%Y')
                info['year'] = release.year

        add_dir(
            name=movie['title'].encode('utf-8'),
            method='load_movie',
            icon='{}/{}'.format(__TMDB_IMAGE_BASE__, movie['poster_path']),
            fanart='{}/{}'.format(__TMDB_IMAGE_BASE__, movie['backdrop_path']) if 'backdrop_path' in movie else '',
            description=movie['overview'].encode('utf-8') if 'overview' in movie else '',
            page='1',
            data=movie['id'],
            is_playable=True,
            info=info
        )


def show_tvs(tvs):
    for tv in tvs:
        if not tv['poster_path']:
            continue

        info = {
            'title': tv['name'].encode('utf-8'),
            'plot': '[B]??rt??kel??s: {}[/B] '.format(tv['vote_average'] if 'vote_average' in tv else 0) + (
                tv['overview'].encode('utf-8') if 'overview' in tv else ''),
            'originaltitle': tv['original_name'].encode('utf-8') if 'original_name  ' in tv else '',
            'genre': [__TV_GENRES__[genre_id] for genre_id in tv['genre_ids']] if 'genre_ids' in tv else 'Egy??b',
            'rating': tv['vote_average'] if 'vote_average' in tv else 0
        }

        if 'first_air_date' in tv:
            release = tv['first_air_date'].split('-')
            if len(release) == 3 and int(release[0]) >= 1900:
                release = datetime.datetime(int(release[0]), int(release[1]), int(release[2]))
                info['date'] = release.strftime('%d.%m.%Y')
                info['year'] = release.year

        add_dir(
            name=tv['name'].encode('utf-8'),
            method='load_tv',
            icon='{}/{}'.format(__TMDB_IMAGE_BASE__, tv['poster_path']),
            fanart='{}/{}'.format(__TMDB_IMAGE_BASE__, tv['backdrop_path']) if 'backdrop_path' in tv else '',
            description=tv['overview'].encode('utf-8') if 'overview' in tv else '',
            page='1',
            data=tv['id'],
            is_playable=True,
            info=info
        )


def load_tv():
    try:
        tv_id = int(params['data'])
        tvs.load_tv(tv_id)
    except Exception as e:
        xbmcgui.Dialog().ok('error', e.message)


def load_movie():
    try:
        movie_id = int(params['data'])
        movies.load_movie(movie_id)
    except Exception as e:
        xbmcgui.Dialog().ok('error', e.message)


def add_dir(name, method, icon, fanart, description, page, data=None, is_playable=False, info=None, position=None):
    icon = icon if re.match(r'^http(s)?:\/\/.*', icon) else get_media(icon)
    fanart = fanart if re.match(r'^http(s)?:\/\/.*', fanart) else get_media(fanart)
    data = str({}) if data is None else data
    query = {'method': method, 'data': data, 'page': page}
    url = "{base}?{query}".format(base=sys.argv[0], query=build_query(query))

    if info is None:
        info = {'title': name, 'plot': description}

    list_item = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
    list_item.setInfo(type="Video", infoLabels=info)
    list_item.setProperty("Fanart_Image", fanart)
    if position:
        list_item.setProperty('specialsort', position)
    if is_playable:
        list_item.setProperty('IsPlayable', 'true')
        list_item.setProperty('isFolder', 'false')
        list_item.setContentLookup(False)
        list_item.setArt({'icon': icon, 'thumb': icon, 'poster': icon, 'fanart': fanart})
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=list_item, isFolder=True)


def movie_sort_by():
    data = json.loads(base64.b64decode(params['data']))
    search_params = data['search_params']
    engine_name = data['engine']
    context_menu = [
        '[B][COLOR yellow]{}[/COLOR][/B]'.format(__SORT__['movie'][engine_name][option]['name']) if option ==
                                                                                                    search_params[
                                                                                                        'sort_by'] else
        __SORT__['movie'][engine_name][option]['name'] for option in __SORT__['movie'][engine_name].keys()]
    menu_index = dialog.contextmenu(context_menu)
    if menu_index > -1:
        search_params['sort_by'] = __SORT__['movie'][engine_name].keys()[menu_index]
        search_params['page'] = 1
        movie_list(engine_name, search_params, 1)
        finalise('movie_list')
        xbmc.executebuiltin(
            'Container.SetSortMethod({})'.format(__SORT__['movie'][engine_name][search_params['sort_by']]['kodi']))
        if re.search(r'\.desc', search_params['sort_by']):
            xbmc.executebuiltin('Container.SetSortDirection')


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
                list_of_params[slices[0]] = urllib.unquote(slices[1])
    return list_of_params


def finalise(method, args=None):
    if method in ['load_movie', 'load_tv', 'movie_sort_by', 'tv_sort_by']:
        return

    xbmcplugin.endOfDirectory(int(sys.argv[1]))

    list_views = ['movie_folder', 'tv_folder', 'main_folders']

    if method in list_views or method is None:
        xbmc.executebuiltin('Container.SetViewMode({})'.format(55))
    else:
        xbmc.executebuiltin('Container.SetViewMode({})'.format(51))

    if method in ['movie_random']:
        xbmc.executebuiltin('Container.SetSortMethod({})'.format(KODI_SORT_METHOD_RATING))
        xbmc.executebuiltin('Container.SetSortDirection')


params = get_params()

try:
    method = params["method"]
    locals()[method]()
except:
    method = None
    main_folders()

if method != 'movie_list':
    finalise(method)
