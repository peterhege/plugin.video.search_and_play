import json
import os
import xbmc
import xbmcaddon

AVAILABLE_FILE = os.path.join(xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('profile')).decode('utf-8'),
                              'download.json')

if not os.path.exists(AVAILABLE_FILE):
    with open(AVAILABLE_FILE, 'w') as df:
        json.dump({}, df)

with open(AVAILABLE_FILE, 'r') as df:
    search = json.load(df)


def search_job(tmdb_id, languages, download, qualities=None):
    if not languages or type(languages) != list:
        languages = []
    if not qualities or type(qualities) != list:
        qualities = []
    if tmdb_id not in search:
        search[tmdb_id] = {"qualities": [], "languages": []}

    search[tmdb_id] = {
        "qualities": list(set(search[tmdb_id]['qualities'] + qualities)),
        "languages": list(set(search[tmdb_id]['languages'] + languages)),
        "download": bool(download)
    }

    with open(AVAILABLE_FILE, 'w') as df:
        json.dump(search, df)
