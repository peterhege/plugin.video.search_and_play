# -*- coding: utf-8 -*-
import re

import requests

from .base import Qbittorrent
from .model import TorrentCollection, Torrent, TorrentType, TrackerCollection, Tracker, WebSeedCollection, \
    TorrentFileCollection

try:
    from typing import Union, List
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
        'add': '/add'
    }

    def search(self, params):  # type: (InfoParams) -> TorrentCollection
        return self.info(params)

    def info(self, params):  # type: (InfoParams) -> TorrentCollection
        path = self._get_path('info')
        params = {k: v for k, v in params.__dict__.items() if v is not None}
        return TorrentCollection(self._GET(path, params))

    def get(self, hash):  # type: (str) -> Union[TorrentType,None]
        return self.properties(hash)

    def properties(self, hash):  # type: (str) -> Union[TorrentType,None]
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
        return TrackerCollection(self._GET(path, {'hash': hash}))

    def web_seeds(self, hash):  # type: (str) -> WebSeedCollection
        path = self._get_path('webseeds')
        return WebSeedCollection(self._GET(path, {'hash': hash}))

    def files(self, hash, indexes=None):  # type: (str,Union[str,List[str]]) -> TorrentFileCollection
        path = self._get_path('files')
        params = {'hash': hash}
        if indexes is not None:
            if type(indexes) is list:
                indexes = '|'.join(indexes)
            params['indexes'] = indexes
        return TorrentFileCollection(self._GET(path, params))

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
        if type(hashes) is list:
            hashes = '|'.join(hashes)
        path = self._get_path('reannounce')
        params = {'hashes': hashes}
        return self._GET(path, params)

    def add(
            self,
            torrent_file=None,  # type: str
            urls=None,  # type: Union[list,str]
            savepath=None,  # type: str
            cookie=None,  # type: str
            category=None,  # type: str
            tags=None,  # type: str
            skip_checking=None,  # type: str
            paused=None,  # type: bool
            root_folder=None,  # type: str
            rename=None,  # type: str
            upLimit=None,  # type: int
            dlLimit=None,  # type: int
            ratioLimit=None,  # type: float
            seedingTimeLimit=None,  # type: int
            autoTMM=None,  # type: bool
            sequentialDownload=None,  # type: bool
            firstLastPiecePrio=None,  # type: bool
    ):
        if torrent_file is None and urls is None:
            raise Exception("Required parameters: 'torrent_file' or 'urls'")

        ignored = ['self', 'torrent_file', 'urls']
        payload = {k: v for k, v in locals().iteritems() if k not in ignored and v is not None}
        if 'urls' in payload:
            payload['urls'] = '\n'.join(payload['urls']) if type(payload['urls']) is list else payload['urls']
        if 'tags' in payload:
            payload['tags'] = ','.join(payload['tags']) if type(payload['tags']) is list else payload['tags']

        params = {}
        if len(payload.values()):
            params['payload'] = payload
        if torrent_file is not None:
            buffer = open(torrent_file, 'rb')
            params['files'] = {'torrents': buffer}

        path = self._get_path('add')

        return self._POST(path, **params)

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


Torrent.driver = Torrents
Tracker.driver = Torrents
