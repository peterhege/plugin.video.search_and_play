from .base import Qbittorrent


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
        torrents (dict): Property: torrent hash, value: same as torrent list
        torrents_removed (list): List of hashes of torrents removed since last request
        categories (dict): Info for categories added since last request
        categories_removed (list): List of categories removed since last request
        tags (list): List of tags added since last request
        tags_removed (list): List of tags removed since last request
        server_state (dict): Global transfer info
        trackers (dict):
    """
    rid = None  # type: int
    full_update = None  # type: bool
    torrents = None  # type: dict
    torrents_removed = None  # type: list
    categories = None  # type: dict
    categories_removed = None  # type: list
    tags = None  # type: list
    tags_removed = None  # type: list
    server_state = None  # type: dict
    trackers = None  # type: dict

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
