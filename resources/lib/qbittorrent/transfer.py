from .base import Qbittorrent
from .model import TransferInfo

try:
    from typing import Union, List
except:
    pass


class Transfer(Qbittorrent):
    BASE_PATH = 'transfer'
    URLS = {
        'info': '/info',
        'speedLimitsMode': '/speedLimitsMode',
        'toggleSpeedLimitsMode': '/toggleSpeedLimitsMode',
        'downloadLimit': '/downloadLimit',
        'setDownloadLimit': '/setDownloadLimit',
        'uploadLimit': '/uploadLimit',
        'setUploadLimit': '/setUploadLimit',
        'banPeers': '/banPeers'
    }

    def info(self):
        """https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-(qBittorrent-4.1)#get-global-transfer-info"""
        path = self._get_path('info')
        params = {k: v for k, v in locals().iteritems() if v is not None and k != 'self'}
        return TransferInfo(**self._GET(path, params))

    def speed_limits_mode(self, toggle=False):  # type: (bool) -> bool
        if toggle:
            return self.toggle_speed_limits_mode()
        return self.get_speed_limits_mode()

    def get_speed_limits_mode(self):  # type: () -> bool
        path = self._get_path('speedLimitsMode')
        return bool(int(self._GET(path)))

    def toggle_speed_limits_mode(self):  # type: () -> bool
        path = self._get_path('toggleSpeedLimitsMode')
        self._GET(path)
        return self.get_speed_limits_mode()

    def download_limit(self, limit=None):  # type: (int) -> int
        if limit is None:
            return self.get_download_limit()
        return self.set_download_limit(limit)

    def get_download_limit(self):  # type: () -> int
        path = self._get_path('downloadLimit')
        return int(self._GET(path))

    def set_download_limit(self, limit):  # type: (int) -> int
        path = self._get_path('setDownloadLimit')
        self._GET(path, {"limit": limit})
        return self.get_download_limit()

    def upload_limit(self, limit=None):  # type: (int) -> int
        if limit is None:
            return self.get_upload_limit()
        return self.set_upload_limit(limit)

    def get_upload_limit(self):  # type: () -> int
        path = self._get_path('uploadLimit')
        return int(self._GET(path))

    def set_upload_limit(self, limit):  # type: (int) -> int
        path = self._get_path('setUploadLimit')
        self._GET(path, {"limit": limit})
        return self.get_upload_limit()

    def ban_peers(self, peers):  # type: (Union[str,List[str]]) -> bool
        """
        :param peers: The peer to ban, or multiple peers separated by a pipe |. Each peer is a colon-separated host:port
        """
        if not self.version_satisfying('2.3.0'):
            raise Exception('Min version 2.3.0')

        peers = '|'.join(peers) if type(peers) is list else peers

        try:
            path = self._get_path('banPeers')
            self._GET(path, {"peers": peers})
            return True
        except:
            return False
