# -*- coding: utf-8 -*-

from . import TorrentCollection, CategoryCollection, TrackerCollection

try:
    from typing import Dict, List
except:
    pass


class SyncData(object):
    """
    https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-(qBittorrent-4.1)#get-main-data

    Parameters:
        rid (int): Response ID
        full_update (bool): Whether the response contains all the data or partial data
        torrents (TorrentCollection): Property: torrent hash, value: same as torrent list
        torrents_removed (list): List of hashes of torrents removed since last request
        categories (Categories): Info for categories added since last request
        categories_removed (list): List of categories removed since last request
        tags (list): List of tags added since last request
        tags_removed (list): List of tags removed since last request
        server_state (ServerState): Global transfer info
        trackers (Trackers):
    """
    rid = None  # type: int
    full_update = None  # type: bool
    torrents = None  # type: TorrentCollection
    torrents_removed = None  # type: list
    categories = None  # type: CategoryCollection
    categories_removed = None  # type: list
    tags = None  # type: list
    tags_removed = None  # type: list
    server_state = None  # type: ServerState
    trackers = None  # type: TrackerCollection

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setter = 'set_{}'.format(k)
            if hasattr(self, setter) and callable(getattr(self, setter)):
                setter = getattr(self, setter)
                setter(v)
            else:
                setattr(self, k, v)

    def set_trackers(self, trackers):  # type: (Dict[str,List[str]]) -> SyncData
        self.trackers = TrackerCollection(trackers)
        return self

    def set_server_state(self, server_state):  # type: (dict) -> SyncData
        self.server_state = ServerState(**server_state)
        return self

    def set_torrents(self, torrents):  # type: (Dict[str,dict]) -> SyncData
        self.torrents = TorrentCollection(torrents)
        return self

    def set_categories(self, categories):  # type: (Dict[str,Dict[str,str]]) -> SyncData
        self.categories = CategoryCollection(categories)
        return self


class ServerState(object):
    average_time_queue = None,  # type: int
    free_space_on_disk = None,  # type: int
    queued_io_jobs = None,  # type: int
    up_info_data = None,  # type: int
    connection_status = None,  # type: str
    global_ratio = None,  # type: str
    up_rate_limit = None,  # type: int
    dl_info_data = None,  # type: int
    use_alt_speed_limits = None,  # type: bool
    total_buffers_size = None,  # type: int
    refresh_interval = None,  # type: int
    dl_rate_limit = None,  # type: int
    up_info_speed = None,  # type: int
    total_wasted_session = None,  # type: int
    alltime_dl = None,  # type: int
    queueing = None,  # type: bool
    total_peer_connections = None,  # type: int
    dht_nodes = None,  # type: int
    dl_info_speed = None,  # type: int
    total_queued_size = None,  # type: int
    read_cache_hits = None,  # type: str
    alltime_ul = None,  # type: int
    write_cache_overload = None,  # type: str
    read_cache_overload = None,  # type: str

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
