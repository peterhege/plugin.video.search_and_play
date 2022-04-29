from .base import Qbittorrent, to_snake_case


class Transfer(Qbittorrent):
    BASE_PATH = 'transfer'
    URLS = {
        'info': '/info',
        'speedLimitsMode': '/speedLimitsMode',
        'toggleSpeedLimitsMode': '/toggleSpeedLimitsMode',
        'downloadLimit': '/downloadLimit',
        'setDownloadLimit': '/setDownloadLimit'
    }

    def info(self):
        """https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-(qBittorrent-4.1)#get-global-transfer-info"""
        path = self._get_path('info')
        params = {k: v for k, v in locals().iteritems() if v is not None and k != 'self'}
        return Info(**self._GET(path, params))

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


class Info(object):
    dl_info_speed = None  # type: int
    dl_info_data = None  # type: int
    up_info_speed = None  # type: int
    up_info_data = None  # type: int
    dl_rate_limit = None  # type: int
    up_rate_limit = None  # type: int
    dht_nodes = None  # type: int
    connection_status = None  # type: str

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, to_snake_case(k), v)
