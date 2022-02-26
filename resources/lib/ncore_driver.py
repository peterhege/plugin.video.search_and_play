# -*- coding: utf-8 -*-
import base64
import json
import os
import pickle
import re
import shutil
import xbmc
import xbmcaddon
import xbmcgui
import requests
from resources.lib import settings_repository, context_factory, available_manager
from resources.lib.control import setting
import htmlement

try:
    sys
except:
    import sys

session = None
base_url = 'https://ncore.pro'
endpoint = lambda endpoint: '{base}/{endpoint}.php'.format(base=base_url, endpoint=endpoint)
cookie_file_name = os.path.join(
    xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('profile')).decode('utf-8'),
    'ncore.cookie'
)
CACHE_DIR = os.path.join(xbmcaddon.Addon().getAddonInfo('path'), 'cache')
TORRENT_CACHE_DIR = os.path.join(CACHE_DIR, 'torrents')
LANGUAGES = {
    'hun': 'Magyar',
    'eng': 'Angol'
}
QUALITIES = ['SD', '720p', '1080p', '2160p']
TMDB_DATA = []
if not os.path.exists(CACHE_DIR):
    os.mkdir(CACHE_DIR)
if not os.path.exists(TORRENT_CACHE_DIR):
    os.mkdir(TORRENT_CACHE_DIR)


def for_movie(tmdb_data):
    return tmdb_data


def context(tmdb_data):
    global TMDB_DATA
    TMDB_DATA = tmdb_data
    string = json.dumps(tmdb_data)
    b64 = base64.b64encode(string)
    context_key = 'ncore_driver.check({})'.format(b64)
    return {context_key: 'Letöltés'}


def check(tmdb_data):
    from resources.lib import qbittorrent_driver
    (user, pwd) = (setting('ncore_user'), setting('ncore_pass'))
    if not login(user, pwd):
        (user, pwd) = (settings_repository.setting('ncore_user'), settings_repository.setting('ncore_pass'))
        i = 0
        while not login(user, pwd):
            if i == 5:
                xbmcgui.Dialog().ok('Bejelentkezési hiba', '{} sikertelen próbálkozás. Próbáld meg később.'.format(i))
                return
            xbmcgui.Dialog().notification(
                'Bejelentkezési hiba',
                'Hibás felhasználónév vagy jelszó!',
                xbmcgui.NOTIFICATION_ERROR
            )
            (user, pwd) = get_auth()
            if not user or not pwd:
                return
            i += 1

    tmdb_data = json.loads(base64.b64decode(tmdb_data))
    qbittorrent_driver.TMDB_DATA = tmdb_data
    torrents = search_movie(tmdb_data)
    if torrents:
        return language_menu(base64.b64encode(json.dumps(torrents)))

    search_job(tmdb_data['id'])


def search_job(tmdb_id, language=None, quality=None):
    looking = xbmcgui.Dialog().yesno(
        'Nem található!', 'Figyeljem hogy mikor elérhető?'
    )
    if not looking:
        return
    will_download = xbmcgui.Dialog().yesno(
        'Figyelni fogok!', 'Ha elérhető, akkor mit tegyek?',
        yeslabel='Letöltés', nolabel='Csak értesítés'
    )
    if not language:
        languages = xbmcgui.Dialog().multiselect('Nyelv', LANGUAGES.values())
        languages = [LANGUAGES.keys()[i] for i in range(len(LANGUAGES.keys())) if i in languages]
    else:
        languages = [language]
    qualities = []
    if will_download:
        if not quality:
            qualities = xbmcgui.Dialog().multiselect('Felbontás', QUALITIES)
            qualities = [QUALITIES[i] for i in range(len(QUALITIES)) if i in qualities]
        else:
            qualities = [quality]
    available_manager.search_job(tmdb_id, languages, will_download, qualities)
    xbmcgui.Dialog().ok('Kész', 'Szólok ha találok valamit ;)')


def login(user, pwd):
    global session
    if session is None:
        user_agent = 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.6 Safari/537.36'
        session = requests.Session()
        session.headers.update({'User-Agent': user_agent})

    if os.path.isfile(cookie_file_name):
        cookie_file = open(cookie_file_name)
        cookies = requests.utils.cookiejar_from_dict(pickle.load(cookie_file))
        session.cookies = cookies

    valid_str = user + ' profilja'

    response = session.get(endpoint('profile'))
    if valid_str not in response.content:
        payload = {'nev': user, 'pass': pwd, 'ne_leptessen_ki': True}
        session.post(endpoint('login'), data=payload)
        response = session.get(endpoint('profile'))
        if valid_str in response.content:
            cookie_file = open(cookie_file_name, 'w')
            pickle.dump(requests.utils.dict_from_cookiejar(session.cookies), cookie_file)
            return True
        return False
    return True


def get_auth():
    user = xbmcgui.Dialog().input('nCore Felhasználónév')
    setting('ncore_user', user)
    if not user:
        return user, None
    pwd = xbmcgui.Dialog().input('nCore Jelszó')
    setting('ncore_pass', pwd)
    return user, pwd


def search_movie(tmdb_data, pages=None, found=None, second=None):
    from resources.lib import qbittorrent_driver
    qbittorrent_driver.REPLACE_FILE_NAME = '{title} {year}'.format(
        title=tmdb_data['title'].encode('utf-8'),
        year=tmdb_data['release_date'].encode('utf-8')[:4]
    )
    page = 1 if pages is None else pages.pop(0)

    if not found and page > 10:
        return found

    title = second if second else tmdb_data['title']
    title = title.lower().replace(' ', '.').encode('utf-8')
    url = '{endpoint}?miszerint=seeders&hogyan=DESC&tipus=kivalasztottak_kozott&kivalasztott_tipus=xvid,hd,xvid_hun,hd_hun&mire={query}&oldal={page}' \
        .format(endpoint=endpoint('torrents'), query=title, page=page)
    root = htmlement.fromstring(get_content(url))

    if pages is None:
        pages = [
            int(re.search('oldal=([0-9]+)', a.get('href')).group(1))
            for a in root.iterfind('.//*[@id="pager_bottom"]/a') if
            re.match('.*oldal=[0-9]+.*$', a.get('href'))
        ]
        if len(pages):
            pages = list(range(2, pages[-1] + 1))

    rows = root.findall('.//*[@class="box_torrent"]')

    if not len(rows):
        return found if second else search_movie(tmdb_data, None, found, tmdb_data['original_title'])

    found = found if found else {}
    for row in rows:
        try:
            torrent_a = row.find('.//*[@class="torrent_txt"]/a')
            torrent_id = re.search('id=([0-9]+)', torrent_a.get('href')).group(1)
            imdb_id = re.search(
                r'https:\/\/imdb.com\/title\/([a-z0-9]+)', row.find('.//a[@class="infolink"]').get('href')
            ).group(1)
            if imdb_id and imdb_id != tmdb_data['imdb_id'].encode('utf-8'):
                continue
            language = match(re.search(r'hun$', row.find('.//*[@class="box_alap_img"]/a').get('href')), 'eng')
            torrent_title = [
                re.search('[1-9][0-9]*[pi]', torrent_a.text if torrent_a.text else torrent_a.find('nobr').text),
                re.search('[1-9][0-9]*[pi]', row.find('.//*[@class="siterank"]/span').text)
            ]
            torrent_title = [m.group() for m in torrent_title if m]
            quality = torrent_title[0] if torrent_title else 'SD'

            key = '{}:{}'.format(language, quality)
            if key not in found:
                found[key] = torrent_id
        except Exception as e:
            xbmc.log('ncore_driver.py [183] {}'.format(e.message), xbmc.LOGWARNING)
            continue

    if len(pages) > 0:
        return search_movie(tmdb_data, pages, found, second)
    if not second:
        return search_movie(tmdb_data, None, found, tmdb_data['original_title'])
    return found


def language_menu(torrents):
    prev_key = 'ncore_driver.language_menu({torrents})'.format(torrents=torrents)
    torrents = json.loads(base64.b64decode(torrents))
    menu = {}
    languages = {}
    for key in torrents.keys():
        (language, quality) = key.split(':')
        language_text = LANGUAGES[language.lower()]
        if language not in languages:
            languages[language] = {}
        languages[language][torrents[key]] = quality if quality == 'SD' else 'HD {}'.format(quality)
        menu[language] = '[B]{lang}[/B] ({count})'.format(lang=language_text, count=len(languages[language].values()))

    context_menu = {}
    for language in LANGUAGES:
        if language in menu:
            menu_key = 'ncore_driver.download_menu({b64},{language})'.format(
                b64=base64.b64encode(json.dumps(languages[language])),
                language=language
            )
            context_menu[menu_key] = menu[language]
        else:
            menu_key = 'ncore_driver.search_job({id},{language})'.format(id=TMDB_DATA['id'], language=language)
            context_menu[menu_key] = '[COLOR red][B]{lang}[/B][/COLOR] (Nincs)'.format(lang=LANGUAGES[language.lower()])

    context_factory.show(context_menu, prev_key)


def download_menu(qualities, language):
    qualities = json.loads(base64.b64decode(qualities))
    menu = {}
    for torrent_id in qualities:
        menu_key = 'ncore_driver.download({torrent_id})'.format(torrent_id=torrent_id)
        menu[menu_key] = qualities[torrent_id]

    for quality in QUALITIES:
        if quality not in qualities.values() and 'HD {}'.format(quality) not in qualities.values():
            menu_key = 'ncore_driver.search_job({id},{language},{quality})'.format(
                id=TMDB_DATA['id'], language=language, quality=quality
            )
            menu[menu_key] = '[COLOR red][B]{quality}[/B][/COLOR] (Nincs)'.format(quality=quality)

    context_factory.show(menu)


def match(m, default=None):
    return m.group() if m and m.group() else default


def download(torrent_id):
    try:
        from resources.lib import qbittorrent_driver
        url = '{endpoint}?action=details&id={torrent_id}'.format(endpoint=endpoint('torrents'), torrent_id=torrent_id)
        root = htmlement.fromstring(get_content(url))
        key = re.search('key=([0-9a-z]+)', root.find('.//*[@class="download"]/a').get('href')).group(1)

        download_url = '{endpoint}?action=download&id={torrent_id}&key={key}' \
            .format(endpoint=endpoint('torrents'), torrent_id=torrent_id, key=key)

        content = session.get(download_url, stream=True)
        content.raw.decode_content = True

        torrent_file = os.path.join(TORRENT_CACHE_DIR, '{}.torrent'.format(torrent_id))

        output = open(torrent_file, 'wb')
        shutil.copyfileobj(content.raw, output)
        output.close()

        save_path = setting('qbittorrent_movies_path')
        if not save_path:
            save_path = xbmcgui.Dialog().input('qBittorrent Filmek mappa')
            if save_path:
                setting('qbittorrent_movies_path', save_path)
            else:
                return
        qbittorrent_driver.start(torrent_file, save_path, 'movies')
    except Exception as e:
        xbmcgui.Dialog().notification('nCore Hiba', e.message, xbmcgui.NOTIFICATION_ERROR)


def get_content(url):
    try:
        content = session.get(url).content
    except AttributeError:
        content = session.get(url, verify=False).content

    return content
