# -*- coding: utf-8 -*-
import json
import re

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
            if k == 'tags':
                v = [tag.strip() for tag in v.split(',')]
            setattr(self, to_snake_case(k), v)

    def __getattr__(self, item):
        return Torrent.driver()._extend(self, item)

    def update(self, torrent):  # type: (Torrent) -> TorrentType
        for k, v in torrent.__dict__.items():
            if v is not None:
                setattr(self, k, v)
        return self

    def pieces(self):  # type: () -> Union[TorrentPieceCollection, None]
        if not self.piece_hashes:
            return None
        return TorrentPieceCollection([{
            'index': i,
            'hash': self.piece_hashes[i],
            'state': self.piece_states[i]
        } for i in range(len(self.piece_hashes))])

    def pause(self):
        Torrent.driver().pause(self.hash)
        return self

    def resume(self):
        Torrent.driver().resume(self.hash)
        return self

    def delete(self, delete_files=False):
        Torrent.driver().delete(self.hash, delete_files)
        return self

    def recheck(self):
        Torrent.driver().recheck(self.hash)
        return self

    def do_reannounce(self):
        Torrent.driver().reannounce(self.hash)
        return self

    def add_trackers(self, urls):  # type: (Union[str,List[str]]) -> Torrent
        Torrent.driver().add_trackers(self.hash, urls)
        return self

    def edit_tracker(self, original_url, new_url):  # type: (str,str) -> Torrent
        Torrent.driver().edit_tracker(self.hash, original_url, new_url)
        return self

    def remove_trackers(self, urls):  # type: (Union[str,List[str]]) -> Torrent
        Torrent.driver().remove_trackers(self.hash, urls)
        return self

    def peer_list(self):  # type: () -> TorrentPeerCollection
        collection = Torrent.sync().torrent_peers(self.hash)  # type: TorrentPeerCollection
        return collection

    def add_peers(self, peers):  # type: (Union[List[TorrentPeer],str,List[str],TorrentPeer]) -> Torrent
        Torrent.driver().add_peers(self.hash, peers)
        return self

    def increase_priority(self):  # type: () -> Torrent
        Torrent.driver().increase_priority(self.hash)
        if self.priority is not None:
            self.priority += 1
        return self

    def decrease_priority(self):  # type: () -> Torrent
        Torrent.driver().decrease_priority(self.hash)
        if self.priority is not None:
            self.priority -= 1
        return self

    def top_priority(self):  # type: () -> Torrent
        Torrent.driver().top_priority(self.hash)
        self.priority = 1
        return self

    def bottom_priority(self):  # type: () -> Torrent
        Torrent.driver().bottom_priority(self.hash)
        self.priority = Torrent.driver().download_limit(self.hash)[self.hash]
        return self

    def set_download_limit(self, limit):  # type: (int) -> Torrent
        Torrent.driver().set_download_limit(self.hash, limit)
        self.dl_limit = limit
        return self

    def set_share_limit(self, ratio_limit, seeding_time_limit):  # type: (float, int) -> Torrent
        Torrent.driver().set_share_limits(self.hash, ratio_limit, seeding_time_limit)
        self.ratio_limit = ratio_limit
        self.seeding_time_limit = seeding_time_limit
        return self

    def set_upload_limit(self, limit):  # type: (int) -> Torrent
        Torrent.driver().set_upload_limit(self.hash, limit)
        self.up_limit = limit
        return self

    def set_location(self, location):  # type: (str) -> Torrent
        Torrent.driver().set_location(self.hash, location)
        self.save_path = location
        return self

    def rename(self, name):  # type: (str) -> Torrent
        Torrent.driver().rename(self.hash, name)
        self.name = name
        return self

    def set_category(self, category):  # type: (str) -> Torrent
        Torrent.driver().set_category(self.hash, category)
        self.category = category
        return self

    def add_tags(self, tags):  # type: (Union[str,List[str]]) -> Union[Torrent,TorrentType]
        Torrent.driver().add_tags(self.hash, tags)
        if self.tags is None:
            self.tags = ''
        if type(tags) is str:
            tags = tags.split(',')
        self.tags = list(set(self.tags + tags))
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
    piece_states = None  # type: List[int]
    piece_hashes = None  # type: List[str]


class CategoryCollection(Collection):
    list = []  # type: List[Category]

    def __init__(self, data_list):  # type: (Dict[str,Dict[str,str]]) -> None
        super(CategoryCollection, self).__init__(data_list.values(), Category)

    def find_by_name(self, name):  # type: (str) -> Union[Category,None]
        return self.search(lambda c: c.name == name)


class Category(object):
    name = None  # type: str
    save_path = None  # type: str

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, to_snake_case(k), v)

    def set_save_path(self, save_path):  # type: (str) -> Category
        Torrent.driver().edit_category(self.name, save_path)
        self.save_path = save_path
        return self

    def remove(self):
        Torrent.driver().remove_categories(self.name)
        return self


class TrackerCollection(Collection):
    list = []  # type: List[Tracker]
    torrent_hash = None  # type: str

    def __init__(self, trackers, torrent_hash):  # type: (Union[Dict[str,List[str]],List[dict]],str) -> None
        self.torrent_hash = torrent_hash
        trackers = self.parse(trackers)
        super(TrackerCollection, self).__init__(trackers, Tracker)

    def parse(self, trackers):
        if type(trackers) is dict:
            trackers_dict = trackers.copy()
            trackers = []
            for url, hashes in trackers_dict.items():
                data = {'url': url, 'hashes': hashes}
                trackers.append(data)
        for tracker in trackers:
            tracker['torrent_hash'] = self.torrent_hash
        return trackers

    def add(self, urls):  # type: (Union[str,List[str]]) -> TrackerCollection
        Torrent.driver().add_trackers(self.torrent_hash, urls)
        self.list = Torrent.driver().trackers(self.torrent_hash).list
        return self


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
    torrent_hash = None  # type: str

    def __init__(self, **kwargs):  # type: (dict) -> None
        for k, v in kwargs.items():
            setattr(self, k, v)

    def edit(self, url):  # type: (str) -> Tracker
        Torrent.driver().edit_tracker(self.torrent_hash, self.url, url)
        self.url = url
        return self

    def remove(self):  # type: () -> Tracker
        Torrent.driver().remove_trackers(self.torrent_hash, self.url)
        return self


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
    PRIOR_DISABLE = 0
    PRIOR_NORMAL = 1
    PRIOR_HIGH = 6
    PRIOR_MAX = 7

    index = None  # type: int
    name = None  # type: str
    size = None  # type: int
    progress = None  # type: float
    priority = None  # type: int
    is_seed = None  # type: bool
    piece_range = None  # type: int
    availability = None  # type: float
    torrent_hash = None  # type: str

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def set_priority(self, priority):  # type: (int) -> TorrentFile
        Torrent.driver().file_priority(self.torrent_hash, self.index, priority)
        self.priority = priority
        return self


class TorrentFileCollection(Collection):
    list = []  # type: List[TorrentFile]

    def __init__(self, data_list, torrent_hash):
        for index in range(len(data_list)):
            if 'index' not in data_list[index]:
                data_list[index]['index'] = index
            data_list[index]['torrent_hash'] = torrent_hash
        super(TorrentFileCollection, self).__init__(data_list, TorrentFile)

    def movie_file(self):  # type: () -> Union[TorrentFile,None]
        video = r'\.(webm|mkv|flv|vob|ogv|ogg|drc|mng|avi|mov|wmv|mp4)$'
        files = filter(lambda f: re.search(video, f.name) and not re.search(r'sample', f.name), self.list)
        if len(files) == 0:
            return None
        return sorted(files, key=lambda f: f.size, reverse=True)[0]


class TorrentPieceCollection(Collection):
    list = []  # type: List[TorrentPiece]

    def __init__(self, data_list):
        super(TorrentPieceCollection, self).__init__(data_list, TorrentPiece)


class TorrentPiece(object):
    index = None
    state = None
    hash = None

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
