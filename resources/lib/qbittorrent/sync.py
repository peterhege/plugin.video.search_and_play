from .base import Qbittorrent
from .model import SyncData, TorrentPeerCollection

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

    def main_data(self, rid=None):  # type: (int) -> SyncData
        """
        Get main data

        Parameters:
             rid (int): Response ID. If not provided, rid=0 will be assumed. If the given rid is different from the one
                        of last server reply, full_update will be true (see the server reply details for more info)
        """
        path = self._get_path('mainData')
        params = {k: v for k, v in locals().iteritems() if v is not None and k != 'self'}
        return SyncData(**self._GET(path, params))

    def torrent_peers(self, hash, rid=None):  # type: (str,int)-> TorrentPeers
        """
        Get torrent peers data

        Parameters:
            hash (str): Torrent hash
            rid (int): Response ID. If not provided, rid=0 will be assumed. If the given rid is different from the one
                        of last server reply, full_update will be true (see the server reply details for more info)
        """
        path = self._get_path('torrentPeers')
        params = {k: v for k, v in locals().iteritems() if v is not None and k != 'self'}
        return TorrentPeerCollection(**self._GET(path, params))
