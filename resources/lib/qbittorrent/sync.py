from .base import Qbittorrent, to_snake_case

try:
    from typing import List, Dict, Union
except:
    pass


class Sync(Qbittorrent):
    """Sync API implements requests for obtaining changes since the last request."""

    BASE_PATH = 'sync'
    URLS = {
        'mainData': '/maindata',
        'torrentPeers': '/torrentPeers',
    }

    def main_data(self, rid=None):  # type: (int) -> MainData
        """
        Get main data

        Parameters:
             rid (int): Response ID. If not provided, rid=0 will be assumed. If the given rid is different from the one
                        of last server reply, full_update will be true (see the server reply details for more info)
        """
        path = self._get_path('mainData')
        params = {k: v for k, v in locals().iteritems() if v is not None and k != 'self'}
        return MainData(**self._GET(path, params))

    def torrent_peers(self):
        pass


class MainData(object):
    """
    https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-(qBittorrent-4.1)#get-main-data

    Parameters:
        rid (int): Response ID
        full_update (bool): Whether the response contains all the data or partial data
        torrents (Torrents): Property: torrent hash, value: same as torrent list
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
    torrents = None  # type: Torrents
    torrents_removed = None  # type: list
    categories = None  # type: Categories
    categories_removed = None  # type: list
    tags = None  # type: list
    tags_removed = None  # type: list
    server_state = None  # type: ServerState
    trackers = None  # type: Trackers

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setter = 'set_{}'.format(k)
            if hasattr(self, setter) and callable(getattr(self, setter)):
                setter = getattr(self, setter)
                setter(v)
            else:
                setattr(self, k, v)

    def set_trackers(self, trackers):  # type: (Dict[str,List[str]]) -> MainData
        self.trackers = Trackers(trackers)
        return self

    def set_server_state(self, server_state):  # type: (dict) -> MainData
        self.server_state = ServerState(**server_state)
        return self

    def set_torrents(self, torrents):  # type: (Dict[str,dict]) -> MainData
        self.torrents = Torrents(torrents)
        return self

    def set_categories(self, categories):  # type: (Dict[str,Dict[str,str]]) -> MainData
        self.categories = Categories(categories)
        return self


class Trackers(object):
    trackers = []  # type: List[Tracker]

    def __init__(self, trackers_dict):  # type: (Dict[str,List[str]]) -> None
        self.trackers = [Tracker(url, hashes) for url, hashes in trackers_dict.items()]

    def search(self, needle):  # type: (str) -> List[Tracker]
        return [tracker for tracker in self.trackers if needle in tracker.url]


class Tracker(object):
    url = None  # type: str
    hashes = []  # type: List[str]

    def __init__(self, url, hashes):  # type: (str,List[str]) -> None
        self.url = url
        self.hashes = hashes


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


class Torrents(object):
    torrents = []  # type: List[Torrent]

    def __init__(self, torrents_dict):  # type: (Dict[str,dict]) -> None
        self.torrents = [Torrent(hash, **data) for hash, data in torrents_dict.items()]

    def find_by_hash(self, needle):  # type: (str) -> Torrent
        for torrent in self.torrents:
            if needle == torrent.hash:
                return torrent
        return None


class Torrent(object):
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

    def __init__(self, hash, **kwargs):  # type: (str,dict) -> None
        self.hash = hash
        for k, v in kwargs.items():
            setattr(self, k, v)


class Categories(object):
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
