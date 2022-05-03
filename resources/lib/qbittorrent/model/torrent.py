# -*- coding: utf-8 -*-
import json

from .base import Collection
from ..functions import to_snake_case

try:
    from typing import List, Dict, Union
except:
    pass


class TorrentCollection(Collection):
    list = []  # type: List[TorrentType]

    def __init__(self, torrents):  # type: (Union[List[dict],Dict[str,dict]]) -> None
        if type(torrents) is dict:
            torrents_dict = torrents.copy()
            torrents = []
            for hash, data in torrents_dict.items():
                data['hash'] = hash if 'hash' not in data else data['hash']
                torrents.append(data)
        super(TorrentCollection, self).__init__(torrents, Torrent)

    def find_by_hash(self, needle):  # type: (str) -> TorrentType
        torrent = self.search(lambda t: t.hash == needle)  # type: TorrentType
        return torrent


class Torrent(object):
    STATE_ERROR = 'error'
    STATE_MISSING_FILES = 'missingFiles'
    STATE_UPLOADING = 'uploading'
    STATE_PAUSED_UP = 'pausedUP'
    STATE_QUEUED_UP = 'queuedUP'
    STATE_STALLED_UP = 'stalledUP'
    STATE_CHECKING_UP = 'checkingUP'
    STATE_FORCED_UP = 'forcedUP'
    STATE_ALLOCATING = 'allocating'
    STATE_DOWNLOADING = 'downloading'
    STATE_META_DL = 'metaDL'
    STATE_PAUSED_DL = 'pausedDL'
    STATE_QUEUED_DL = 'queuedDL'
    STATE_STALLED_DL = 'stalledDL'
    STATE_CHECKING_DL = 'checkingDL'
    STATE_FORCED_DL = 'forcedDL'
    STATE_CHECKING_RESUME_DATA = 'checkingResumeData'
    STATE_MOVING = 'moving'
    STATE_UNKNOWN = 'unknown'

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __getattr__(self, item):
        return Torrent.driver()._extend(self, item)

    def update(self, torrent):  # type: (Torrent) -> TorrentType
        for k, v in torrent.__dict__.items():
            if v is not None:
                setattr(self, k, v)
        return self


class TorrentType(Torrent):
    hash = None  # type: str
    num_incomplete = None,  # type: int
    force_start = None,  # type: bool
    upspeed = None,  # type: int
    completion_on = None,  # type: int
    seen_complete = None,  # type: int
    num_leechs = None,  # type: int
    auto_tmm = None,  # type: bool
    last_activity = None,  # type: int
    seeding_time = None,  # type: int
    seq_dl = None,  # type: bool
    trackers_count = None,  # type: int
    dl_limit = None,  # type: int
    availability = None,  # type: int
    size = None,  # type: int
    category = None,  # type: str
    max_seeding_time = None,  # type: int
    ratio = None,  # type: float
    time_active = None,  # type: int
    total_size = None,  # type: int
    priority = None,  # type: int
    state = None,  # type: str
    tracker = None,  # type: str
    num_seeds = None,  # type: int
    ratio_limit = None,  # type: int
    progress = None,  # type: int
    up_limit = None,  # type: int
    magnet_uri = None,  # type: str
    uploaded = None,  # type: int
    save_path = None,  # type: str
    tags = None,  # type: str
    completed = None,  # type: int
    max_ratio = None,  # type: int
    downloaded = None,  # type: int
    seeding_time_limit = None,  # type: int
    amount_left = None,  # type: int
    downloaded_session = None,  # type: int
    uploaded_session = None,  # type: int
    dlspeed = None,  # type: int
    num_complete = None,  # type: int
    name = None,  # type: str
    content_path = None,  # type: str
    f_l_piece_prio = None,  # type: bool
    super_seeding = None,  # type: bool
    eta = None,  # type: int
    added_on = None  # type: int
    creation_date = None  # type: int
    piece_size = None  # type: int
    comment = None  # type: str
    total_wasted = None  # type: int
    total_uploaded = None  # type: int
    total_uploaded_session = None  # type: int
    total_downloaded = None  # type: int
    total_downloaded_session = None  # type: int
    nb_connections = None  # type: int
    nb_connections_limit = None  # type: int
    share_ratio = None  # type: float
    addition_date = None  # type: int
    completion_date = None  # type: int
    created_by = None  # type: str
    dl_speed_avg = None  # type: int
    dl_speed = None  # type: int
    last_seen = None  # type: int
    peers = None  # type: int
    peers_total = None  # type: int
    pieces_have = None  # type: int
    pieces_num = None  # type: int
    reannounce = None  # type: int
    seeds = None  # type: int
    seeds_total = None  # type: int
    up_speed_avg = None  # type: int
    trackers = None  # type: TrackerCollection
    web_seeds = None  # type: WebSeedCollection
    files = None  # type: TorrentFileCollection


class CategoryCollection(object):
    categories = []  # type: List[Category]

    def __init__(self, categories_dict):  # type: (Dict[str,Dict[str,str]]) -> None
        self.categories = [Category(**data) for data in categories_dict.values()]

    def search(self, needle):  # type: (str) -> List[Category]
        return [category for category in self.categories if needle in category.name]


class Category(object):
    name = None  # type: str
    save_path = None  # type: str

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, to_snake_case(k), v)


class TrackerCollection(Collection):
    list = []  # type: List[Tracker]

    def __init__(self, trackers):  # type: (Union[Dict[str,List[str]],List[dict]]) -> None
        if type(trackers) is dict:
            trackers_dict = trackers.copy()
            trackers = []
            for url, hashes in trackers_dict.items():
                data = {'url': url, 'hashes': hashes}
                trackers.append(data)
        super(TrackerCollection, self).__init__(trackers, Tracker)


class Tracker(object):
    url = None  # type: str
    hashes = None  # type: List[str]
    status = None  # type: int
    tier = None  # type: int
    num_peers = None  # type: int
    num_seeds = None  # type: int
    num_leeches = None  # type: int
    num_downloaded = None  # type: int
    msg = None  # type: str

    def __init__(self, **kwargs):  # type: (dict) -> None
        for k, v in kwargs.items():
            setattr(self, k, v)


class TorrentPeerCollection(object):
    peers = None  # type: List[TorrentPeer]
    rid = None  # type: int
    full_update = None  # type: bool
    show_flags = None  # type: bool

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setter = 'set_{}'.format(k)
            if hasattr(self, setter) and callable(getattr(self, setter)):
                setter = getattr(self, setter)
                setter(v)
            else:
                setattr(self, k, v)

    def set_peers(self, peers_dict):  # type: (dict) -> TorrentPeerCollection
        self.peers = [TorrentPeer(**peer) for peer in peers_dict.values()]
        return self

    def find_by_ip(self, ip):  # type: (str) -> List[TorrentPeer]
        return [peer for peer in self.peers if peer.ip == ip]


class TorrentPeer:
    dl_speed = None,  # type: int
    files = None,  # type: str
    uploaded = None,  # type: int
    country = None,  # type: str
    up_speed = None,  # type: int
    port = None,  # type: int
    downloaded = None,  # type: int
    connection = None,  # type: str
    client = None,  # type: str
    flags = None,  # type: str
    country_code = None,  # type: str
    ip = None,  # type: str
    relevance = None,  # type: int
    progress = None,  # type: int
    flags_desc = None,  # type: str

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, to_snake_case(k), v)


class WebSeed(object):
    url = None  # type: str

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class WebSeedCollection(Collection):
    list = []  # type: List[WebSeed]

    def __init__(self, data_list):
        super(WebSeedCollection, self).__init__(data_list, WebSeed)


class TorrentFile(object):
    index = None  # type: int
    name = None  # type: str
    size = None  # type: int
    progress = None  # type: float
    priority = None  # type: int
    is_seed = None  # type: bool
    piece_range = None  # type: int
    availability = None  # type: float

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class TorrentFileCollection(Collection):
    list = []  # type: List[TorrentFile]

    def __init__(self, data_list):
        super(TorrentFileCollection, self).__init__(data_list, TorrentFile)
