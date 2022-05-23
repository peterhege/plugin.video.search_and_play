# -*- coding: utf-8 -*-
import re

import requests

from .base import Qbittorrent
from .model import TorrentCollection, Torrent, TorrentType, TrackerCollection, Tracker, WebSeedCollection, \
    TorrentFileCollection, TorrentPeer, CategoryCollection, Category

try:
    from typing import Union, List, Dict
except:
    pass


class Torrents(Qbittorrent):
    BASE_PATH = 'torrents'
    URLS = {
        'info': '/info',
        'properties': '/properties',
        'trackers': '/trackers',
        'webseeds': '/webseeds',
        'files': '/files',
        'pieceStates': '/pieceStates',
        'pieceHashes': '/pieceHashes',
        'pause': '/pause',
        'resume': '/resume',
        'delete': '/delete',
        'recheck': '/recheck',
        'reannounce': '/reannounce',
        'add': '/add',
        'addTrackers': '/addTrackers',
        'editTracker': '/editTracker',
        'removeTrackers': '/removeTrackers',
        'addPeers': '/addPeers',
        'increasePrio': '/increasePrio',
        'decreasePrio': '/decreasePrio',
        'topPrio': '/topPrio',
        'bottomPrio': '/bottomPrio',
        'filePrio': '/filePrio'
    }

    def search(self, params):  # type: (InfoParams) -> TorrentCollection
        return self.info(params)

    def info(self, params):  # type: (InfoParams) -> TorrentCollection
        params = {k: v for k, v in params.__dict__.items() if v is not None}
        if 'hashes' in params and not self.version_satisfying('2.0.1'):
            raise Exception('Required WebUI API version is 2.0.1 for hashes parameter.')
        if 'filter' in params and params['filter'] in [
            InfoParams.FILTER_STALLED, InfoParams.FILTER_STALLED_UPLOADING, InfoParams.FILTER_STALLED_DOWNLOADING
        ] and not self.version_satisfying('2.4.1'):
            raise Exception('Min version 2.4.1')
        path = self._get_path('info')
        result = self._GET(path, params)
        if 'tag' in params and not self.version_satisfying('2.8.3'):
            result = filter(lambda d: params['tag'] in d['tags'].split(', '), result)
        return TorrentCollection(result)

    def get(self, hash):  # type: (str) -> Union[TorrentType,Torrent]
        return Torrent(hash=hash)

    def properties(self, hash):  # type: (str) -> Union[TorrentType,None,Torrent]
        path = self._get_path('properties')
        try:
            torrent = Torrent(**self._GET(path, {'hash': hash}))
            torrent.hash = hash
            return torrent
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise e

    def last_added(self):  # type: () -> Union[TorrentType,None]
        torrents = self.search(InfoParams(sort=InfoParams.SORT_ADDED_ON, limit=1, reverse=True))
        if torrents.is_empty():
            return None
        return torrents.first()

    def trackers(self, hash):  # type: (str) -> TrackerCollection
        path = self._get_path('trackers')
        return TrackerCollection(self._GET(path, {'hash': hash}), hash)

    def web_seeds(self, hash):  # type: (str) -> WebSeedCollection
        path = self._get_path('webseeds')
        return WebSeedCollection(self._GET(path, {'hash': hash}))

    def files(self, hash, indexes=None):  # type: (str,Union[str,List[str]]) -> TorrentFileCollection
        params = {'hash': hash}
        if indexes is not None:
            if type(indexes) is list:
                indexes = '|'.join(indexes)
            params['indexes'] = indexes

        path = self._get_path('files')
        result = self._GET(path, params)

        if not self.version_satisfying('2.8.2') and indexes is not None:
            indexes = indexes.split('|')
            r = []
            for index in range(len(result)):
                if index in indexes:
                    r = result[index]
                    r[index]['index'] = index
            result = r

        return TorrentFileCollection(result, hash)

    def piece_states(self, hash):
        path = self._get_path('pieceStates')
        params = {'hash': hash}
        return self._GET(path, params)

    def piece_hashes(self, hash):
        path = self._get_path('pieceHashes')
        params = {'hash': hash}
        return self._GET(path, params)

    def pause(self, hashes):
        if type(hashes) is list:
            hashes = '|'.join(hashes)
        path = self._get_path('pause')
        params = {'hashes': hashes}
        return self._GET(path, params)

    def resume(self, hashes):
        if type(hashes) is list:
            hashes = '|'.join(hashes)
        path = self._get_path('resume')
        params = {'hashes': hashes}
        return self._GET(path, params)

    def delete(self, hashes, delete_files=False):
        if type(hashes) is list:
            hashes = '|'.join(hashes)
        path = self._get_path('delete')
        params = {'hashes': hashes, 'deleteFiles': delete_files}
        return self._GET(path, params)

    def recheck(self, hashes):
        if type(hashes) is list:
            hashes = '|'.join(hashes)
        path = self._get_path('recheck')
        params = {'hashes': hashes}
        return self._GET(path, params)

    def reannounce(self, hashes):
        if not self.version_satisfying('2.0.2'):
            raise Exception('Required WebUI API version is 2.0.2 for reannounce method')
        if type(hashes) is list:
            hashes = '|'.join(hashes)
        path = self._get_path('reannounce')
        params = {'hashes': hashes}
        return self._GET(path, params)

    def add(
            self,
            torrent_files=None,  # type: Union[str,List[str]]
            urls=None,  # type: Union[list,str]
            save_path=None,  # type: str
            cookie=None,  # type: str
            category=None,  # type: str
            tags=None,  # type: str
            skip_checking=None,  # type: bool
            paused=None,  # type: bool
            root_folder=None,  # type: bool
            rename=None,  # type: str
            upload_limit=None,  # type: int
            download_limit=None,  # type: int
            ratio_limit=None,  # type: float
            seeding_time_limit=None,  # type: int
            automatic_torrent_management=None,  # type: bool
            sequential_download=None,  # type: bool
            first_last_piece_prior=None,  # type: bool
    ):  # type: (...) -> Torrent
        """
        Arguments:
            urls (str): URLs separated with newlines
            torrent_files (list): Raw data of torrent file. torrents can be presented multiple times.
            save_path (str): [optional] Download folder
            cookie (str): [optional] Cookie sent to download the .torrent file
            category (str): [optional] Category for the torrent
            tags (str): [optional] Tags for the torrent, split by ','
            skip_checking (bool): [optional] Skip hash checking. Possible values are true, false (default)
            paused (bool): [optional] Add torrents in the paused state. Possible values are true, false (default)
            root_folder (bool): [optional] Create the root folder. Possible values are true, false, unset (default)
            rename (str): [optional] Rename torrent
            upload_limit (int): [optional] Set torrent upload speed limit. Unit in bytes/second
            download_limit (int): [optional] Set torrent download speed limit. Unit in bytes/second
            ratio_limit (float): [optional] since 2.8.1 Set torrent share ratio limit
            seeding_time_limit (int): [optional] since 2.8.1 Set torrent seeding time limit. Unit in seconds
            automatic_torrent_management (bool): [optional] Whether Automatic Torrent Management should be used
            sequential_download (bool): [optional] Enable sequential download. Possible values are true, false (default)
            first_last_piece_prior (bool): [optional] Prioritize download first last piece. Possible values are true, false (default)
        """
        if torrent_files is None and urls is None:
            raise Exception("Required parameters: 'torrent_file' or 'urls'")

        if (ratio_limit is not None or seeding_time_limit is not None) and not self.version_satisfying('2.8.1'):
            raise Exception('Required WebUI API version is 2.8.1 for ratio_limit and seeding_time_limit parameters.')
        if automatic_torrent_management is not None and not self.version_satisfying('2.2.0'):
            raise Exception('Min version 2.2.0')

        payload = {}
        key_dict = {
            'save_path': 'savepath',
            'upload_limit': 'upLimit',
            'download_limit': 'dlLimit',
            'ratio_limit': 'ratioLimit',
            'seeding_time_limit': 'seedingTimeLimit',
            'automatic_torrent_management': 'autoTMM',
            'sequential_download': 'sequentialDownload',
            'first_last_piece_prior': 'firstLastPiecePrio'
        }
        for k, v in locals().iteritems():
            if k in ['self', 'torrent_file']:
                continue
            if k in key_dict:
                k = key_dict[k]
            if k == 'url':
                v = '\n'.join(v) if type(v) is list else v
            elif k == 'tags':
                v = ','.join(v) if type(v) is list else v
            payload[k] = v

        params = {}
        if len(payload.values()):
            params['payload'] = payload
        if torrent_files is not None:
            if type(torrent_files) is str:
                torrent_files = [torrent_files]
            params['files'] = [('torrents', open(torrent_file, 'rb')) for torrent_file in torrent_files]

        path = self._get_path('add')
        self._POST(path, **params)
        return self.last_added()

    def add_trackers(self, hash, urls):  # type: (str,Union[str,List[str]]) -> None
        path = self._get_path('addTrackers')
        if type(urls) is list:
            urls = '\n'.join(urls)
        payload = {'hash': hash, 'urls': urls}
        return self._POST(path, payload=payload)

    def edit_tracker(self, hash, original_url, new_url):  # type: (str,str,str) -> None
        if not self.version_satisfying('2.2.0'):
            raise Exception('Required WebUI API version is 2.2.0 for edit_tracker method')
        path = self._get_path('editTracker')
        payload = {'hash': hash, 'origUrl': original_url, 'newUrl': new_url}
        return self._POST(path, payload=payload)

    def remove_trackers(self, hash, urls):  # type: (str,Union[str,List[str]]) -> None
        if not self.version_satisfying('2.2.0'):
            raise Exception('Required WebUI API version is 2.2.0 for remove_trackers method')
        path = self._get_path('removeTrackers')
        if type(urls) is list:
            urls = '\n'.join(urls)
        payload = {'hash': hash, 'urls': urls}
        return self._POST(path, payload=payload)

    def add_peers(
            self,
            hashes,  # type: Union[str,List[str]]
            peers  # type: Union[List[TorrentPeer],str,List[str],TorrentPeer]
    ):
        # type: (...) -> None
        """
        Arguments:
            hashes (str): The hash of the torrent, or multiple hashes separated by a pipe |
            peers (str): The peer to add, or multiple peers separated by a pipe |. Each peer is a colon-separated host:port
        """
        if not self.version_satisfying('2.3.0'):
            raise Exception('Min version 2.3.0')
        if type(hashes) is list:
            hashes = '|'.join(hashes)
        if type(peers) is list:
            peers = '|'.join(['{}:{}'.format(p.ip, p.port) if type(p) is TorrentPeer else p for p in peers])
        path = self._get_path('addPeers')
        payload = {'hashes': hashes, 'peers': peers}
        return self._POST(path, payload=payload)

    def increase_priority(self, hashes):  # type: (Union[str,List[str]]) -> None
        if type(hashes) is list:
            hashes = '|'.join(hashes)
        path = self._get_path('increasePrio')
        payload = {'hashes': hashes}
        return self._POST(path, payload=payload)

    def decrease_priority(self, hashes):  # type: (Union[str,List[str]]) -> None
        if type(hashes) is list:
            hashes = '|'.join(hashes)
        path = self._get_path('decreasePrio')
        payload = {'hashes': hashes}
        return self._POST(path, payload=payload)

    def top_priority(self, hashes):  # type: (Union[str,List[str]]) -> None
        if type(hashes) is list:
            hashes = '|'.join(hashes)
        path = self._get_path('topPrio')
        payload = {'hashes': hashes}
        return self._POST(path, payload=payload)

    def bottom_priority(self, hashes):  # type: (Union[str,List[str]]) -> None
        if type(hashes) is list:
            hashes = '|'.join(hashes)
        path = self._get_path('bottomPrio')
        payload = {'hashes': hashes}
        return self._POST(path, payload=payload)

    def file_priority(self, hash, id, priority):  # type: (str,Union[int,List[int]],int) -> None
        if type(id) is list:
            if self.version_satisfying('2.2.0'):
                id = '|'.join(id)
            else:
                raise Exception('Min version 2.2.0')

        path = self._get_path('filePrio')
        payload = {'hash': hash, 'id': id, 'priority': priority}
        return self._POST(path, payload=payload)

    def download_limit(self, hashes):  # type: (Union[str,List[str]]) -> Dict[str,int]
        if type(hashes) is list:
            hashes = '|'.join(hashes)
        path = self._get_path('/downloadLimit')
        params = {'hashes': hashes}
        return self._GET(path, params=params)

    def set_download_limit(self, hashes, limit):  # type: (Union[str,List[str]],int) -> None
        """
        Parameters:
            hashes: hashes can contain multiple hashes separated by | or set to all
            limit: limit is the download speed limit in bytes per second
        """
        if type(hashes) is list:
            hashes = '|'.join(hashes)
        path = self._get_path('/setDownloadLimit')
        payload = {'hashes': hashes, 'limit': limit}
        return self._POST(path, payload=payload)

    def set_share_limits(self, hashes, ratio_limit, seeding_time_limit):
        # type: (Union[str,List[str]], float, int) -> None
        """
        Parameters:
            hashes: can contain multiple hashes separated by | or set to all
            ratio_limit: is the max ratio the torrent should be seeded until. -2 means the global limit should be used, -1 means no limit.
            seeding_time_limit: is the max amount of time the torrent should be seeded. -2 means the global limit should be used, -1 means no limit.
        """
        if not self.version_satisfying('2.0.1'):
            raise Exception('Required WebUI API version is 2.0.1 for set_share_limits method')
        path = self._get_path('/setShareLimits')
        payload = {'hashes': hashes, 'ratioLimit': ratio_limit, 'seedingTimeLimit': seeding_time_limit}
        return self._POST(path, payload=payload)

    def upload_limit(self, hashes):
        if type(hashes) is list:
            hashes = '|'.join(hashes)
        path = self._get_path('/uploadLimit')
        params = {'hashes': hashes}
        return self._GET(path, params=params)

    def set_upload_limit(self, hashes, limit):  # type: (Union[str,List[str]],int) -> None
        """
        Parameters:
            hashes: can contain multiple hashes separated by | or set to all
            limit: is the upload speed limit in bytes per second you want to set.
        """
        if type(hashes) is list:
            hashes = '|'.join(hashes)
        path = self._get_path('/setUploadLimit')
        payload = {'hashes': hashes, 'limit': limit}
        return self._POST(path, payload=payload)

    def set_location(self, hashes, location):  # type: (Union[str,List[str]],str) -> None
        if type(hashes) is list:
            hashes = '|'.join(hashes)
        path = self._get_path('/setLocation')
        payload = {'hashes': hashes, 'location': location}
        return self._POST(path, payload=payload)

    def rename(self, hash, name):  # type: (str,str) -> None
        path = self._get_path('/rename')
        payload = {'hash': hash, 'name': name}
        return self._POST(path, payload=payload)

    def set_category(self, hashes, category):  # type: (Union[str,List[str]],str) -> None
        if type(hashes) is list:
            hashes = '|'.join(hashes)
        if self.categories().find_by_name(category) is None:
            self.create_category(category)
        path = self._get_path('/setCategory')
        payload = {'hashes': hashes, 'category': category}
        return self._POST(path, payload=payload)

    def category(self, name):  # type: (str) -> Union[Category,None]
        return self.categories().find_by_name(name)

    def categories(self):  # type: () -> CategoryCollection
        if not self.version_satisfying('2.1.1'):
            raise Exception('Required WebUI API version is 2.1.1 for categories method')
        path = self._get_path('/categories')
        return CategoryCollection(self._GET(path))

    def create_category(self, name, save_path=None):  # type: (str,str) -> None
        path = self._get_path('/createCategory')
        payload = {'category': name}
        if save_path is not None:
            if not self.version_satisfying('2.1.0'):
                raise Exception('Required WebUI API version is 2.1.0 for save_path parameter.')
            payload['savePath'] = save_path
        return self._POST(path, payload=payload)

    def edit_category(self, name, save_path):  # type: (str,str) -> None
        if not self.version_satisfying('2.1.0'):
            raise Exception('Required WebUI API version is 2.1.0 for edit_category method')
        path = self._get_path('/editCategory')
        payload = {'category': name, 'savePath': save_path}
        return self._POST(path, payload=payload)

    def _extend(self, torrent, key):  # type: (TorrentType,str) -> ...
        _torrent = None
        if key in [
            'up_speed_avg', 'addition_date', 'comment', 'completion_date', 'created_by', 'creation_date', 'dl_speed',
            'dl_speed_avg', 'last_seen', 'nb_connections', 'nb_connections_limit', 'peers', 'peers_total', 'piece_size',
            'pieces_have', 'pieces_num', 'reannounce', 'seeds', 'seeds_total', 'share_ratio', 'total_downloaded',
            'total_downloaded_session', 'total_uploaded', 'total_uploaded_session', 'total_wasted'
        ]:
            _torrent = self.properties(torrent.hash)
        if key in [
            'added_on', 'amount_left', 'auto_tmm', 'availability', 'category', 'completed', 'completion_on',
            'content_path', 'dlspeed', 'downloaded', 'downloaded_session', 'f_l_piece_prio', 'force_start',
            'last_activity', 'magnet_uri', 'max_ratio', 'max_seeding_time', 'name', 'num_complete', 'num_incomplete',
            'num_leechs', 'num_seeds', 'priority', 'progress', 'ratio', 'ratio_limit', 'seeding_time_limit',
            'seen_complete', 'seq_dl', 'size', 'state', 'super_seeding', 'tags', 'time_active', 'tracker',
            'trackers_count', 'uploaded', 'uploaded_session', 'upspeed'
        ]:
            torrents = self.search(InfoParams(hashes=torrent.hash))
            if not torrents.is_empty():
                _torrent = torrents.first()
        if key == 'piece_states':
            states = self.piece_states(torrent.hash)
            _torrent = Torrent(piece_states=states)
        if key == 'piece_hashes':
            hashes = self.piece_hashes(torrent.hash)
            _torrent = Torrent(piece_hashes=hashes)
        if key == 'trackers':
            trackers = self.trackers(torrent.hash)
            _torrent = Torrent(trackers=trackers)
        if key == 'web_seeds':
            web_seeds = self.web_seeds(torrent.hash)
            _torrent = Torrent(web_seeds=web_seeds)
        if key == 'files':
            files = self.files(torrent.hash)
            _torrent = Torrent(files=files)
        if _torrent is None or not hasattr(_torrent, key):
            return None
        torrent.update(_torrent)
        return getattr(_torrent, key)


class InfoParams(object):
    FILTER_ALL = 'all'
    FILTER_DOWNLOADING = 'downloading'
    FILTER_SEEDING = 'seeding'
    FILTER_COMPLETED = 'completed'
    FILTER_PAUSED = 'paused'
    FILTER_ACTIVE = 'active'
    FILTER_INACTIVE = 'inactive'
    FILTER_RESUMED = 'resumed'
    FILTER_STALLED = 'stalled'
    FILTER_STALLED_UPLOADING = 'stalled_uploading'
    FILTER_STALLED_DOWNLOADING = 'stalled_downloading'
    FILTER_ERRORED = 'errored'

    SORT_ADDED_ON = 'added_on'
    SORT_AMOUNT_LEFT = 'amount_left'
    SORT_AUTO_TMM = 'auto_tmm'
    SORT_AVAILABILITY = 'availability'
    SORT_CATEGORY = 'category'
    SORT_COMPLETED = 'completed'
    SORT_COMPLETION_ON = 'completion_on'
    SORT_CONTENT_PATH = 'content_path'
    SORT_DL_LIMIT = 'dl_limit'
    SORT_DLSPEED = 'dlspeed'
    SORT_DOWNLOADED = 'downloaded'
    SORT_DOWNLOADED_SESSION = 'downloaded_session'
    SORT_ETA = 'eta'
    SORT_F_L_PIECE_PRIO = 'f_l_piece_prio'
    SORT_FORCE_START = 'force_start'
    SORT_HASH = 'hash'
    SORT_LAST_ACTIVITY = 'last_activity'
    SORT_MAGNET_URI = 'magnet_uri'
    SORT_MAX_RATIO = 'max_ratio'
    SORT_MAX_SEEDING_TIME = 'max_seeding_time'
    SORT_NAME = 'name'
    SORT_NUM_COMPLETE = 'num_complete'
    SORT_NUM_INCOMPLETE = 'num_incomplete'
    SORT_NUM_LEECHS = 'num_leechs'
    SORT_NUM_SEEDS = 'num_seeds'
    SORT_PRIORITY = 'priority'
    SORT_PROGRESS = 'progress'
    SORT_RATIO = 'ratio'
    SORT_RATIO_LIMIT = 'ratio_limit'
    SORT_SAVE_PATH = 'save_path'
    SORT_SEEDING_TIME = 'seeding_time'
    SORT_SEEDING_TIME_LIMIT = 'seeding_time_limit'
    SORT_SEEN_COMPLETE = 'seen_complete'
    SORT_SEQ_DL = 'seq_dl'
    SORT_SIZE = 'size'
    SORT_STATE = 'state'
    SORT_SUPER_SEEDING = 'super_seeding'
    SORT_TAGS = 'tags'
    SORT_TIME_ACTIVE = 'time_active'
    SORT_TOTAL_SIZE = 'total_size'
    SORT_TRACKER = 'tracker'
    SORT_UP_LIMIT = 'up_limit'
    SORT_UPLOADED = 'uploaded'
    SORT_UPLOADED_SESSION = 'uploaded_session'
    SORT_UPSPEED = 'upspeed'

    def __init__(self, filter=None, category=None, tag=None, sort=None, reverse=False, limit=None, offset=None,
                 hashes=None, **kwargs):  # type: (str,str,str,str,bool,int,int,str,dict) -> None
        for k, v in locals().iteritems():
            if k == 'kwargs':
                for k2, v2 in v.items():
                    self.setter(k2, v2)
            if k == 'hashes' and type(v) is list:
                v = '|'.join(v)
            if k != 'self':
                self.setter(k, v)

    def setter(self, k, v):
        key_dict = {}
        if k in key_dict.keys():
            k = key_dict[k]
        setattr(self, k, v)
